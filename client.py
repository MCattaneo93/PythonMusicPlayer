#@author - Matthew Cattaneo
import socket
import pyaudio
import tkinter as tk
from tkinter import messagebox
import threading

#default chunk_size
CHUNK_SIZE = 1024
#default width - number of bytes to store each audio sample (16 bits)
WIDTH = 2
#number of audio channels, audio signals (left and right)
CHANNELS = 2
#default Sampling rate
RATE = 44100

#function to take chunks of audio data from server, and write to stream
def receive_songs(my_socket, stream, stop_event):
    # Receive data from the server and play
    
    while not stop_event.is_set():
        data = my_socket.recv(CHUNK_SIZE)
        if not data:
            break
        if data == b'TERMINATE':
            break
    
        stream.write(data)
    
    # Notify that the song transmission has stopped
    stop_event.set()
#event listener method, when the client selects a song, passes the index of the song name selected by the client
def on_select(event, my_socket, stop_event):
    widget = event.widget
    index = int(widget.curselection()[0])
    my_socket.sendall(str(index).encode())
    
    # Create a stop event to signal the end of the song
    stop_event.clear()
#event listener for the stop button, if the user presses stop, distroy the current window
def stop_stream(stop_event, window):
    stop_event.set()
    window.destroy()
#method for creating the window which holds the song list and the stop button
def create_GUI(song_names, my_socket, stop_event):
    window = tk.Tk()
    window.title("Music Player")
    listbox = tk.Listbox(window)
    listbox.pack()
    listbox.bind('<<ListboxSelect>>',lambda event: on_select(event, my_socket, stop_event))
    for song in song_names:
        listbox.insert(tk.END, song)
    
    
    stop_button = tk.Button(window, text="Stop", command=lambda: stop_stream(stop_event, window))
    stop_button.pack()
    
    return window

def main(host, port):
    while True:
        # Connect to the server, default option is TCP
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect((host, port))
        #after a succesful connection, wait for the server to send the list of song names for the widget
        raw_song_names = my_socket.recv(CHUNK_SIZE)
        #convert the bytes into the actual song names
        song_names = eval(raw_song_names.decode())
        
        #open stream, using default values, to play received bytes of audio data
        pa = pyaudio.PyAudio()
        stream = pa.open(format=p.get_format_from_width(WIDTH),
                        channels=CHANNELS,
                        rate=RATE,
                        output=True)
    
        # Create the GUI window
        stop_event = threading.Event()
        window = create_GUI(song_names, my_socket, stop_event)
    
        # Start the thread to receive songs
        receive_song_thread = threading.Thread(target=receive_songs, args=(my_socket, stream, stop_event))
        receive_song_thread.start()
    
        # Run the main event loop
        window.mainloop()
    
        # Wait for the song transmission to complete or stop button to be pressed
        receive_song_thread.join()
    
        # Cleanup
        stream.stop_stream()
        stream.close()
        
        pa.terminate()
        
        # Check if the song was stopped or transmission ended
        if stop_event.is_set():
            messagebox.showinfo("Music Player", "Song stopped. Please pick another")
        else:
            messagebox.showinfo("Music Player", "Song finished. Please pick another")
            

if __name__ == '__main__':
#pass router IP address and port number to main
    main('47.17.19.246', 51782)