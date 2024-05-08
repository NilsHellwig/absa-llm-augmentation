# Master Thesis: Data Augmentation with Large Language Models for Aspect-Based Sentiment Analysis in Low-Resource Scenarios 

In this repository, you will find all resources related to the master's thesis *Data Augmentation with Large Language Models for Aspect-Based Sentiment Analysis in Low-Resource Scenarios.*

## Background

Sentiment analysis (SA), also named opinion mining, is a research area in natural language processing (NLP) which involves the computational classification of individuals' sentiments, opinions and emotions. This mostly involves categorizing sentiments into three polarities: positive, neutral and negative. Social media services like X (formerly known as Twitter) and Facebook have gained popularity as sources of data for SA due to the low barrier for posting messages, enabling a multitude of users around the world to express their opinions on various topics daily. Accordingly, content from social media is used for SA in many fields, for example in the political context, financial sector or healthcare.

Nevertheless, other data sources beside social media are also employed for SA. For example, customer reviews on websites, call center conversations or in-person interviews can serve as valuable sources for discerning user sentiment towards various topics, products and services. SA can be applied at both document- and sentence-level. However, if a document or sentence comprises a mixture of different sentiments, it might not be possible to assign only a positive, negative or neutral label. As an illustrative example, consider a sentence of a restaurant review wherein positive sentiment is expressed towards the food while, concurrently, negative sentiment is expressed when addressing the food's price. To address this issue, Aspect-Based Sentiment Analysis (ABSA) has been extensively studied as it goes beyond assessing general sentiment and instead delves into a more granular examination of sentiment by linking particular aspects with corresponding sentiment polarities.

## Objective

This work aimed to apply LLMs for generating annotated examples for ABSA to reduce data scarcity. A human-annotated dataset of 3,078 sentences from restaurant reviews posted on Tripadvisor in the German language, that can be seen as a low-resource language in ABSA, served as the basis for this study. The annotations covered aspect terms, their corresponding aspect categories and the sentiment expressed towards them. SLMs based on the BERT architecture were fine-tuned for four common ABSA tasks, using increasing amounts of examples (500, 1,000, 1,500) generated by LLMs in addition to a given amount of 500 annotated real examples for training. In the context of this low-resource scenario, it was investigated whether the models' performance could be enhanced by incorporating synthetic examples along with the given 500 real examples. For generating synthetic examples, 25 random samples were drawn from the pool of 500 real examples, serving as few-shot examples in the prompt.

Secondly, an extreme low-resource scenario with a reduced set of only 25 annotated real examples was considered. Increasing amounts of synthetic examples (475, 975, 1,975) were added to the given 25 real examples for training. The given 25 examples were consistently employed as few-shot examples in the prompt for generating all synthetic examples in this low-resource scenario. Here was tested, whether adding synthetic examples to the 25 given real examples for training could achieve comparable performance to models trained exclusively with real examples (500, 1,000, 2,000) for ABSA tasks. 


Two LLMs were evaluated to generate the annotated examples, namely Llama-2-70B and GPT-3.5-turbo, with the prompt comprising a description of the task, 25 few-shot examples and a label. The label comprised one or more combinations of an aspect category and sentiment polarity to be addressed in the generated example. For a given set of training examples, models for the following ABSA tasks were trained: (1) Aspect Category Detection (ACD), (2) Aspect Category Sentiment Analysis (ACSA), (3) End-to-End ABSA (E2E-ABSA) and (4) Target Aspect Sentiment Detection (TASD). Finally, a total of 2,400 human annotations of synthetic examples were employed to assess the quality of annotations generated by LLMs.


## Installation



```bash
pip install -r requirements.txt
python -m spacy download de_core_news_lg
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir
```

## Download Synthetic Dataset

[Google Drive Download](https://drive.google.com/file/d/14zz0eBFEJssVORUB0NGiYx4trwK3oVQJ/view?usp=drive_link)