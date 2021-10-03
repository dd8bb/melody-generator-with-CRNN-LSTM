# coding: utf-8
import os
import json
import music21 as m21 #music converter, usefull to handle with kern,MIDI, musicXML files
import tensorflow.keras as keras
import numpy as np
# VARIABLES


# Path Variables
DEUSTCHL_PATH = "deutschl/"
CHINA_PATH = "china/"
SAVE_DIR = "dataset"
SINGLE_FILE_DATASET = "file_dataset"

# Get all subdirectories and save paths on a list.
german_dataset_paths = []
china_dataset_paths = []

for path, subdir, files in os.walk(DEUSTCHL_PATH):
    for dir in subdir:
        path_to_dir = os.path.join(DEUSTCHL_PATH, dir)
        german_dataset_paths.append(path_to_dir)

for path, subdir, files in os.walk(CHINA_PATH):
    for dir in subdir:
        path_to_dir = os.path.join(CHINA_PATH, dir)
        china_dataset_paths.append(path_to_dir)
        
# Duration variable
ACCEPTABLE_DURATIONS = [
    0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4
]

# Sequence length (Batch size that will feed  our NN)
SEQUENCE_LENGTH = 64
def load_songs_in_kern(dataset_path, songs=None):
    '''Load datasets using music21
       Return a list of music21 objects which each object contain a song
    '''
    if songs == None:
        songs = []
    
    for path, subdir, files in os.walk(dataset_path):
        for file in files:
            if file[-3:] == "krn": #Check for format, don't want to upload other files(checksums)
                song = m21.converter.parse(os.path.join(path,file))
                songs.append(song)
    
    return songs


def has_acceptable_durations(song, acceptable_durations):
    
    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True


def transpose(song):
    '''Transpose  song's pitch to Cmaj/Amin '''
    
    #get key from the song
    parts = song.getElementsByClass(m21.stream.Part)
    measures_part0 =  parts[0].getElementsByClass(m21.stream.Measure)
    key = measures_part0[0][4] # First measure,return list, 4 index is key.
    
    #estimate key using music21
    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")
    
    # get interval for transposition. E.g., Bmaj --> Cmaj
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))
    
    # transpose song by calculated interval
    transposed_song = song.transpose(interval)
    
    return transposed_song


def encode_song(song, time_step=0.25):
    '''Encode song to time-series format'''
    # p = 60, d = 1.0 --> [60, "_", "_", "_"]
    
    encoded_song = []
    
    for event in song.flat.notesAndRests:
        
        # handle notes
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi
        # handle rests
        elif isinstance(event, m21.note.Rest):
            symbol = "r"
        
        # convert the note/rest into time series notation
        steps = int(event.duration.quarterLength / time_step)
        for step in range(steps):
            if step == 0: # First step --> Symbol
                encoded_song.append(symbol)
            else: #Rest of steps are "_"
                encoded_song.append("_")
        
    # cast encoded song to a str
    encoded_song = " ".join(map(str, encoded_song))
    
    return encoded_song


def preprocess(dataset_path, save_dir):
    
    print("Loading songs...")
    if type(dataset_path) == type([]):
        for path in dataset_path:
            try:
                songs = load_songs_in_kern(path, songs=songs)
            except NameError:
                songs = load_songs_in_kern(path)
            finally:
                print(f"Loaded {path} directory.")
    else:
        songs = load_songs_in_kern(dataseth_path)
        
    print(f"Dataset loaded up succesfully. \n Total songs: {len(songs)}")
    
    print(f"Processing songs...")
    for i, song in enumerate(songs):
        if not has_acceptable_durations(song, ACCEPTABLE_DURATIONS):
            continue
        
        #transpose to Cmaj/Amin
        try:
            song = transpose(song)
        except IndexError:
            continue
        #encoded song to time series format
        encoded_song = encode_song(song)
        
        #save songs to text file
        save_path = os.path.join(save_dir, str(i))
        with open(save_path, "w") as file:
            file.write(encoded_song)
    
    print(f"Dataset Created!")
        
        
        
def load_song(file_path):
    with open(file_path, "r") as file:
        song = file.read()
    return song



def create_single_file_dataset(dataset_path, file_dataset_path, sequence_length=SEQUENCE_LENGTH):
    new_song_delimiter = "/ " * sequence_length # Create delimiter with the size of a batch in order to let the network learn that this is the end of a song
    songs = ""
    
    
    # load encoded songs and add delimiters between 
    for path, _ , files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load_song(file_path)
            songs = songs + song + " " + new_song_delimiter
    
    songs = songs[:-1] #Erase last blank
    
    # save string that contains all dataset
    with open(file_dataset_path, "w") as file:
        file.write(songs)
    
    return songs #To later on mapping info from songs
    
    
    
def create_mapping(songs, mapping_path):
    mappings = {}
    
    # identify the vocabulary
    songs = songs.split()
    vocabulary = list(set(songs))
    
    # create mappings (dictionary)
    for i, symbol in enumerate(vocabulary):
        mappings[symbol] = i
    
    
    # save vocabulary to a json file
    with open(mapping_path, "w") as file:
        json.dump(mappings, file)
        
def convert_songs_to_int(songs, mappings_path):
    '''Use of our mapped values for changing the MIDI notation into int values'''
    
    int_songs =[]
    
    #load mappings
    with open(mappings_path, "r") as file:
        mappings = json.load(file)
    
    # cast songs string to a list
    songs = songs.split()
    
    #map songs to int
    for symbol in songs:
        int_songs.append(mappings[symbol])
    
    return int_songs


def generating_training_sequences(dataset, sequence_length=SEQUENCE_LENGTH):
    
    if dataset.lower() == 'china':
        single_file_path = SINGLE_FILE_DATASET + '_China'
        map_path = 'china_mapping.json'
    elif dataset.lower() == 'deutschl':
        single_file_path = SINGLE_FILE_DATASET + '_Deutschl'
        map_path = 'deutschl_mapping.json'
    else:
        print('Wrong Dataset, please check and try again')
        return
    
    # load songs and map them to int
    songs = load_song(single_file_path)
    int_songs = convert_songs_to_int(songs, map_path)
    
    # generate the training sequences
    inputs = []
    targets = []
    
    num_sequences = len(int_songs) - sequence_length
    for  i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_length]) # Each sequence is shifted by one step respect to previous one
        targets.append(int_songs[i+sequence_length]) # Point at the first symbol of next sequence
        
        
    # one-hot encode the sequences
    vocabulary_size = len(set(int_songs)) # Get total num of symbol types in datasets
    inputs = keras.utils.to_categorical(inputs, num_classes=vocabulary_size)
    targets = np.array(targets)
    
    return inputs, targets
    
