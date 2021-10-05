# Melody Generator using CRNN LSTM cells 

Melody Generator based on <a href="https://www.youtube.com/watch?v=FLr0r-QhqH0&list=PL-wATfeyAMNr0KMutwtbeDCmpwvtul-Xz"> Valerio Velardo's Series </a> on melody generator with LSTM.
The training dataset is obtained from <a href="http://www.esac-data.org/"> ESAC dataset </a> which provide folksong from all over the world.


<h4> DATASET </h4>
has been obtained from the ESAC dataset over 6000 german songs and 2000 china (_han, shanxi_) songs. All songs had been preprocess into musical time-series format following Valerio's process.

<h4> MODELS </h4>
Two models trained on each data set for 50 epochs are provided.

<h4> MELODY GENERATOR </h4>
Melody Generator class given on Jupyter notebook.  It has the following syntaxis: <br>

```
melody = mg.generate_melody(seed, num_steps, max_sequence_length, temperature )
```
where:
* seed : First notes of the melody to generate.
* num_steps : max num of steps the neural network can take to generate the melody.
* max_sequence_length : max length the melody can take.
* temperature : float value between [0-1]. The closer to zero, the more predictable the melody will be and viceversa.

<h4> MIDIs </h4>
On midi folder there are few examples I have generated with different temperatures. It sounds pretty neat. you could say it's folk music.
