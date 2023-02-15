# Songwriter.ai

This is an experiment using LSTM (Long short-term memory) neural network to generate new songs.


## Components

### Crawler
Crawler is responsible for crawling lyrics from Genius.com and saving them as a raw file.


### Parser
Parser will extract lyrics from raw files, normalizing and saving them in a structure ready to be used.


### AI Model
Our AI Model will be trained with the lyrics downloaded from Genius and will provide an interface to generate
a new song given an input.