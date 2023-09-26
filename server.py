#@author - Matthew Cattaneo
import socket
import os
import pydub
import glob
import threading

CHUNK_SIZE = 1024
#paths to access song folder
folder_path = os.path.dirname(os.path.abspath(__file__))
song_abs_path = os.path.join(folder_path, 'songs')

#method which accesses all wav files in the song folder and returns the song_names for the client
def get_songs():
    song_files = glob.glob(os.path.join(song_abs_path, '*.wav'))
    song_names = [os.path.basename(file) for file in song_files]
    return song_names

#method which sends the actual chunks of audio data
def send_audio_file(song_name, conn):  
    
    audio = pydub.AudioSegment.from_wav(os.path.join(song_abs_path, song_name))
    wav_data = audio.export(format='wav').read()
    

    for i in range(0, len(wav_data),CHUNK_SIZE):
        chunk = wav_data[i:i + CHUNK_SIZE]
        #print(chunk)
        conn.send(chunk)

    conn.send(b'TERMINATE')

#method which handles the connection of a new client
def process_connection(conn, addr):
    #first obtain song names from the song folder
    song_names = get_songs()
    #send the encoded list over the new connection
    conn.sendall(str(song_names).encode())
    #wait until client sends their selection
    selection = conn.recv(CHUNK_SIZE)
    #decode obtaining the index
    index = int(selection.decode())
    song_name = song_names[index]

    print(f'Accepted connection from {addr}')

    # Send the audio file
    #send_audio_file(song_name, conn)
    send_audio_file(song_name, conn)
    # Clean up the connection
    conn.close()
    print('Connection closed')

def start_server(host, port):
    # Create a socket object
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print(host)

    # Bind the socket to the port
    my_socket.bind((host, port))

    # Listen for incoming connections
    #allow a queue of 5
    my_socket.listen(5)
    print(f'Server listening on {host}:{port}')
    #while loop which handles new client connections
    while True:
        
        # Wait for a connection
        print('Waiting for a connection...')
        conn, addr = my_socket.accept()
        #create a thread for each new client
        client_thread = threading.Thread(target = process_connection, args=(conn,addr))
        client_thread.start()
        
        

if __name__ == '__main__':


    #we start the server listening on '0.0.0.0'
    #because we don't care what network interface it comes over
    #we are looking for the port number
    start_server('0.0.0.0', 51782)
