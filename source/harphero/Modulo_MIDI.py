# 1. inizializzare il sistema MIDI;
# 2. vedere quali dispositivi MIDI sono disponibili;
# 3. individuare/aprire la tastiera che vogliamo utilizzare;
# 4. leggere i messaggi MIDI;
# 5. riconoscere un Note On;
# 6. estrarre il numero della nota;
# 7. trasformare il numero MIDI nel nome della nota;
# 8. restituire al gioco "C4", "F#3", ecc.

import pygame.midi
pygame.midi.init()

all_connected_devices = []

for i in range(pygame.midi.get_count()):
    device = pygame.midi.get_device_info(i)
    if device[2]:
        ID = i 
        all_connected_devices.append(ID)

# chiedo a pygame quali dispositivi MIDI sono disponibili
for i in range(pygame.midi.get_count()):
    print(pygame.midi.get_device_info(i))

# apro la tastiera che voglio utilizzare
input_device = None
midi_devices = []

for ID in all_connected_devices:
    device = pygame.midi.get_device_info(ID)
    device_name = device[1].decode("utf-8", errors="replace")
    midi_devices.append((ID, device_name))

def midi_to_note(note_number):
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    note_name = note_names[note_number % 12]
    octave = note_number // 12 - 1
    return f"{note_name}{octave}"

def select_midi_device(device_id):
    global input_device

    if input_device is not None:
        input_device.close()
        input_device = None

    if device_id is None:
        return

    if device_id not in all_connected_devices:
        return

    try:
        input_device = pygame.midi.Input(device_id)
    except pygame.midi.MidiException as error:
        print("Errore nell'apertura del dispositivo MIDI:", error)

# leggo i messaggi MIDI
def read_midi():
    midi_notes = []
    if input_device is not None:
        if input_device.poll():
            midi_events = input_device.read(10)
            for event in midi_events:
                data = event[0]
                status = data[0]
                note_number = data[1]
                velocity = data[2]
                if status & 0xF0 == 0x90 and velocity > 0:
                    midi_notes.append(midi_to_note(note_number))
    return midi_notes

all_connected_devices = []

for i in range(pygame.midi.get_count()):
    device = pygame.midi.get_device_info(i)
    if device[2]:
        ID = i 
        all_connected_devices.append(ID)

if __name__ == "__main__":
    try:
        while True:
            for note in read_midi():
                print("Nota MIDI ricevuta:", note)
    except KeyboardInterrupt:
        print("Test terminato")
    finally:
        if input_device is not None:
            input_device.close()
        pygame.midi.quit()


