### Note: I'm deprecating this project as I remade it from scratch (with much better results) up for grabs for everyone in https://github.com/matiaszanolli/Auralis

# BLASTbeats

## Remaster your music while you listen to it. Real time.

### Description
BLASTbeats is a tool that allows you to remaster your music while you listen to it. It is based on a modified version of the [Matchering](https://sergree.github.io/matchering/) algorithm. The main difference is that BLASTbeats is designed to work in real time, so you can hear the results of your changes immediately, and will be eventually be embedded into a fully fledge audio player.

### Installation
#### Ubuntu 20.04 LTS
1. Install the necessary dependencies
```
sudo apt update && sudo apt -y install libsndfile1 ffmpeg python3-pip
```
2. Clone the repo and move to the directory
```
git clone https://github.com/matiaszanolli/blastbeats.git && cd blastbeats
```
3. Install dependencies from `requirements.txt`
```
python3 -m pip install -r requirements.txt
```
#### Windows 10
1. Install **[Anaconda Python/R Distribution][anaconda]**
2. Install **[FFmpeg]** to `C:\ffmpeg` and add `C:\ffmpeg\bin` to the PATH variable
3. Run **Anaconda Prompt (Anaconda3)** and move to the cloned `blastbeats` directory
```
cd C:\Users\<your_username>\Downloads\blastbeats
```
4. Install dependencies from `requirements.txt`
```
python -m pip install -r requirements.txt
```

### Usage
BLASTbeats is still in an extremely basic stage. All you can do is pick a song and play it through our engine.

```
python3 blastbeats.py my_song.flac
```

### Credits
- [Matchering](https://sergree.github.io/matchering/) by Sergey Kuznetsov
- [Matchering CLI](https://github.com/sergree/matchering-cli) by Sergey Kuznetsov
- [sounddevice](https://python-sounddevice.readthedocs.io/en/0.4.1/) by Matthias Geier
- [ffmpegio](https://github.com/python-ffmpegio/python-ffmpegio) by Matthew Petroff

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
