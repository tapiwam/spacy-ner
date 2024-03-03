import string, random, re
from .common_tools import *
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import numpy as np

import spacy
from spacy.training.example import Example


import gensim
import multiprocessing
from gensim.models import Word2Vec 
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.test.utils import datapath, get_tmpfile


def clean_and_tokenize_paragraphs_nltk(text):
    nltk_stop_words = set(stopwords.words("english"))
    
    paragraph_with_tokens = []
    for paras in text.split("\n\n"):
        word_token=word_tokenize(paras)
        clean_token=[token for token in word_token if token.casefold() not in nltk_stop_words and token.casefold() not in string.punctuation]
        paragraph_with_tokens.append(clean_token)

    return paragraph_with_tokens


def train_w2v_model(model_name):
    with open('./data/para.json','r',encoding='utf-8') as f:
        texts=json.load(f)
    # print(texts)  
    
    sentences = texts
    
    # Getting the number of cores
    cores = multiprocessing.cpu_count()
    
    # Training the word2vec model
    w2v_model = Word2Vec(min_count=5, # Minimum word count threshold
                     window=2, # The maximum distance between the current and predicted word within a sentence
                     vector_size=500, # Embedding vector size
                     sample=6e-5, # Downsample setting for frequent words
                     alpha=0.03, # Learning rate
                     min_alpha=0.0007, # Minimum learning rate
                     negative=20, # If > 0, negative sampling will be used, the int for negative specifies how many "noise words" should be drown
                     workers=cores-1) # Number of threads to use
    
    # Building the Vocab
    w2v_model.build_vocab(sentences, progress_per=5000)
    
    # Training the model
    w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)
    
    # w2v_model.init_sims(replace=True)
    
    w2v_model.save(f"word_vectors/{model_name}.model")
    w2v_model.wv.save_word2vec_format(f"word_vectors/{model_name}.txt", binary=False)
    print("Training Complete")


def load_keyed_vectors_from_txt(model_path_txt):
    w2v_model = KeyedVectors.load(model_path_txt, binary=False)
    return w2v_model


def spacy_similarity(your_word, model_name):
    nlp = spacy. load (model_name)
    
    ms = nlp. vocab.vectors.most_similar(
        np.asarray([nlp.vocab.vectors[nlp.vocab.strings[your_word]]]), n=10)
    
    words = [nlp.vocab.strings[w] for w in ms [0][0]]
    distances = ms[2]
    print (words)
    
## ==================
## LARGE TEXT CORPUS TOOLS
## =================

def book_basic_clean_text(text):
    cleaned = re.sub(r"[\(\[].*?[\)\]]", "", text)
    return (cleaned)

def build_test_model(nlp_model, text):
    doc = nlp_model(text)
    results = []
    entities = []
    for ent in doc.ents:
        entities.append((ent.start_char, ent.end_char, ent.label_))
    if len(entities) > 0:
        results = [text, {"entities": entities}]
        return (results)

def book_extract_train_data_doublespaced_segments(file_name, chapter_separator="CHAPTER"):
    TRAIN_DATA = []
    
    # New spacy model just for training preparation
    nlp = spacy.blank("en")
    
    with open (file_name, "r")as f:
        text = f.read()

        chapters = text.split(chapter_separator)
        for idx, chapter in enumerate(chapters):
            segments = chapter.split("\n\n")
            hits = []
            for segment in segments:
                segment = segment.strip()
                segment = segment.replace("\n", " ")
                results = build_test_model(nlp, segment)
                if results != None:
                    TRAIN_DATA.append(results)

    return TRAIN_DATA


def train_spacy_ner(model_name, TRAIN_DATA, iterations):
    nlp = spacy.blank("en")

    # Get ner pipeline
    ner = nlp.add_pipe("ner")

    # Iterate over all entities and add labels to NER model - These could be custom
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Find all other pipes and disable them
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.select_pipes(disable=other_pipes):
        
        optimizer = nlp.initialize()
        for itn in range(iterations):
            print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                example = Example.from_dict(nlp.make_doc(text), annotations)
                nlp.update(
                    [example],
                    drop=0.2,
                    sgd=optimizer,
                    losses=losses
                )
            print(f"Losses at iteration {itn} : {losses}")
    
    nlp.to_disk(model_name)

    print(f"Training Complete with {iterations} iterations and {len(TRAIN_DATA)} examples, model saved to {model_name}, the model can be loaded with spacy.load('{model_name}')")
    return nlp