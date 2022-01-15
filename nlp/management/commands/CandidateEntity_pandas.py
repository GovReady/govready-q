#!/usr/bin/env python
# coding: utf-8

from django.core.management.base import BaseCommand

from controls.enums.statements import StatementTypeEnum
from controls.models import Statement, ImportRecord
from controls.utilities import oscalize_control_id
from siteapp.models import User, Project, Organization
# import xlsxio
import os

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


# # Import Libraries

# In[1]:

print("start script")

import spacy    # library spacy used for NLP processing
nlp = spacy.load('en_core_web_sm')  # choose Spacy English Library small
#nlp = spacy.load('en_core_web_lg') # large model
import pandas as pd  # panda library to create dataframes


# References: https://applied-language-technology.readthedocs.io/en/latest/notebooks/part_ii/06_managing_data.html


# # Import Data

# In[2]:


#import excel sheet into pandas

file_name = 'nlp/data/mock_ssp_data.xlsx'  # ENTER YOUR REAL FILENAME HERE!!!!
df = pd.read_excel(file_name)
df


# In[3]:


# Check datatypes


# In[4]:


df.dtypes

print(df.dtypes)

# In[5]:


#create a new column for Spacy processed 'Implementation Statement" data.
df['NLP Implementation Statement'] = None


# # Applying Spacy to process data

# In[6]:


# Apply the language model under 'nlp' to the contents of the DataFrame column 'Implementation Statement'
df['NLP Implementation Statement'] = df['Implementation Statement'].apply(nlp)

# Call the dataframe to check the output
df


# In[7]:


# check Spacy outcome before further processing

df.at[2,'NLP Implementation Statement']


# In[8]:


# check data type for Spacy processed column

type(df.at[2,'NLP Implementation Statement'])


# # Extracting Entities from NLP

# In[9]:


#define our own Python function to fetch Spacy Entities for each Implementation Statement

# Define a function named 'get_Entity' that takes a single object as input.
# We refer to this input using the variable name 'nlp_text'.
def get_Entity(nlp_text):
    
    # First we make sure that the input is of correct type
    # by using the assert command to check the input type
    assert type(nlp_text) == spacy.tokens.doc.Doc
    
    # Let's set up a placeholder list for our Entities
    Entities = []
    
    # We begin then begin looping over the Doc object
    for entity in nlp_text.ents:
        
                   
            # Append entity to the list of entities
            Entities.append(entity.text)
            
    # When the loop is complete, return the list of Entities
    return Entities


# Adapted from Reference code on: https://applied-language-technology.readthedocs.io/en/latest/notebooks/part_ii/06_managing_data.html


# In[10]:


# Apply the 'get_Entity' function to the column 'NLP Implementation Statement''
df['Candidate_Entities'] = df['NLP Implementation Statement'].apply(get_Entity)

# Call the variable to examine the output
df


# # Create New Data Frame with Candidate Entities only

# In[11]:


# list unique candidate entities in document

df['Candidate_Entities'].apply(pd.Series).stack().unique()


# In[12]:


# create new df with candidate entities in document

df2 = df['Candidate_Entities'].apply(pd.Series).stack().unique()
df2


# # Create Dictionary {Candidate Entities: Candidate Entity Sentence}

# In[22]:


#define our own Python function to fetch Spacy Entity and Related Sentence for each Implementation Statement

# Define a function named 'get_EntitySentence' that takes a single object as input.
# We refer to this input using the variable name 'nlp_text'.
def get_EntitySentence(nlp_text):
    
    # First we make sure that the input is of correct type
    # by using the assert command to check the input type
    assert type(nlp_text) == spacy.tokens.doc.Doc
    
    # Let's set up a placeholder dictionary for our Entities
    EntitiesSentencesDict = dict()
    
    # We begin then begin looping over the Doc object
    for entity in nlp_text.ents:
        
                   
            # Create a key and value
            EntitiesSentencesDict[entity.text]= (entity.sent).text  # (add.text to untokenize sentences)
            
    # When the loop is complete, return the list of Entities
    return EntitiesSentencesDict


# In[23]:


# Apply the 'get_EntitySentence' function to the column 'NLP Implementation Statement''
df['Candidate_Entities_with_Sentences'] = df['NLP Implementation Statement'].apply(get_EntitySentence)

# Call the variable to examine the output
df


# In[24]:


# create new dataframe of Candidate Entities and Related Sentences
df3 = df['Candidate_Entities_with_Sentences'].apply(pd.Series)
df3


# In[21]:


df3.dtypes

print(df3.dtypes)

# In[ ]:

print("End of script")
