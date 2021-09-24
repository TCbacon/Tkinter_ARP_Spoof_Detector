from tkinter import *
from tkinter.filedialog import askopenfilename
import os, glob
from pygame import mixer
import subprocess
import time
import threading
from tkinter import messagebox

class Window(object):
    
    def __init__(self,root):
        #inheritance from parent class
        super().__init__()

        self.root = root
        self.root.title("ARP Spoof Detector")
        self.root.geometry('900x600')

        #main app frame
        self.main_app_frame = Frame(root, bg='#c6d9e0')
        self.main_app_frame.grid(row=0, column=0, sticky="news", columnspan=2, ipadx = root.winfo_screenwidth(), ipady = root.winfo_screenheight())

        #stringVar for audio to make it accessible for other wigets to see change
        self.audio_path_stringvar = StringVar()
        self.mac_address_stringvar = StringVar()
        self.ip_address_stringvar = StringVar()

        #audio start and stop boolean
        self.is_test_alert = False
        self.is_program_stopped = False

        #Initialzing pygame mixer
        mixer.init()

        #help page frame
        self.help_frame = Frame(root, bg = '#6e76c1')
        help_to_main_btn = Button(self.help_frame, text='Back',command=lambda:self.back_to_main(self.main_app_frame))
        help_to_main_btn.grid(row=0, column=0)
        about_label = Label(self.help_frame, text="Instructions:\n"+
        "\u2022 Type \'arp -a\' in command prompt to see mac and ip of gateway\n" +
        "\u2022 Add an audio file for alerting ARP spoofing\n" +
        "\u2022 Make sure there are no extra spaces before or after input in the field\n" +
        "\u2022 Press on the start button to initiate the program\n" +
        "\u2022 Press on the start alert test button to test alert sound\n" +
        "\u2022 Press on the stop button to cease the program\n" +
        "\u2022 ARP subprocess call is stored in \'arp_call.txt\'\n" +
        "\u2022 If ARP Spoofing is detected, the spoof info is saved to \'spoof_info_save.txt\'\n" +
        "\u2022 Input field data is saved to \'arp_input_save.txt\' after closing program"
         , font='Helvetica 12 bold', borderwidth=2, relief="solid", justify=LEFT, anchor='w')
        about_label.grid(row=1,column=1)


        #about page frame
        self.about_frame = Frame(self.root, bg = '#9EA097')
        #self.about_frame.grid(row=0, column=0, sticky="news")
        about_to_main_btn = Button(self.about_frame, text='Back',command=lambda:self.back_to_main(self.main_app_frame))
        about_to_main_btn.grid(row=0, column=0)
        about_label = Label(self.about_frame, text="An ARP Spoof Detector", bg = 'white')
        about_label.grid(row=1,column=1)

        #help button
        help_button = Button(self.main_app_frame, text="Help",command=lambda:self.show_help_frame(self.help_frame))
        help_button.grid(row=0, column=0)

        #about button
        about_button = Button(self.main_app_frame, text="About",command=lambda:self.show_about_frame(self.about_frame))
        about_button.grid(row=0, column=1) 
        
        #handles placing the frame over all corners of previous frame using sticky in a for loop
        #alternatively you can use .grid for each of the frames but will be more work
        for frame in (self.main_app_frame, self.about_frame, self.help_frame):
            frame.grid(row=0, column=0, sticky='news')
        
        

        title = Label(self.main_app_frame,text="ARP Spoof Detector")
        title.grid(row=0, column=2, columnspan=3)

        path_label = Label(self.main_app_frame, text="Enter an audio path")
        path_label.grid(row=1, column=3)


        self.path_entry = Entry(self.main_app_frame, textvariable =self.audio_path_stringvar, width=60)
        self.path_entry.grid(row=1, column=4, padx= 30)

        self.select_path_button = Button(self.main_app_frame, text="Pick an audio path", command=self.get_audio_path)
        self.select_path_button.grid(row= 1, column=5)

        
        #enter ip address
        ip_label = Label(self.main_app_frame, text="Enter your gateway ip address")
        ip_label.grid(row=2, column=3)
        self.ip_address_entry = Entry(self.main_app_frame, textvariable=self.ip_address_stringvar, width=60)
        self.ip_address_entry.grid(row=2, column=4)

        #enter mac address
        mac_label = Label(self.main_app_frame, text="Enter your gateway mac address")
        mac_label.grid(row=3, column=3)
        self.mac_address_entry = Entry(self.main_app_frame, textvariable=self.mac_address_stringvar, width=60)
        self.mac_address_entry.grid(row=3, column=4)


        #show if program is running or stopped
        self.program_state = Label(self.main_app_frame, text="Press Start to Run Program", font= "Helvetica 15")
        self.program_state.grid(row=6, column=4, pady=20)

        self.arp_message_label = Label(self.main_app_frame, text="ARP condition" + " Times Checked: 0", font= "Helvetica 15 bold")
        self.arp_message_label.grid(row=7, column=4, pady=30)

        self.start_button = Button(self.main_app_frame, text='Start', command=self.start_arp_detector)
        self.start_button.grid(row= 8, column=3)

        self.test_button = Button(self.main_app_frame, text='Start Alert Test', command=self.test_alert)
        self.test_button.grid(row= 8, column=4)

        self.stop_button = Button(self.main_app_frame, text='Stop',command=self.stop_arp_detector)
        self.stop_button.grid(row=8, column=5) 
        self.stop_button['state'] = 'disabled'


        #init data in entry boxes
        self.read_save_data()

        #initially raise the main app frame
        self.main_app_frame.tkraise()
    

    def read_save_data(self):

        try:
            with open('arp_input_save.txt','r') as save_file:
                entry_list = save_file.readlines()
                length_list = len(entry_list)
                
                for i in range(length_list):
                    if i == 0:
                        #clear entry before inserting new data
                        self.path_entry.delete(0, END)
                        self.path_entry.insert(0, entry_list[i].rstrip('\n'))
                    elif i == 1:
                        #clear entry before inserting new data
                        self.ip_address_entry.delete(0, END)
                        self.ip_address_entry.insert(0, entry_list[i].rstrip('\n'))
                    elif i == 2: 
                        #clear entry before inserting new data
                        self.mac_address_entry.delete(0, END)
                        self.mac_address_entry.insert(0, entry_list[i].rstrip('\n'))                    
                    else:
                        break
        except FileNotFoundError:
            pass

#save the audio, mac and ip fields
    def save_data(self):
        with open('arp_input_save.txt','w') as save_file:
            save_file.write(self.audio_path_stringvar.get() + "\n")
            save_file.write(self.ip_address_stringvar.get() + "\n")
            save_file.write(self.mac_address_stringvar.get() + "\n")
    

    #pre populate the audio path if there is wav or mp3 in current directory
    def prepopulate_audiopath(self):   
        for file in os.listdir("."):
            if file.endswith(".wav") or file.endswith(".mp3"):
                self.path_entry.insert(0, os.path.join(file))
    

    #check if entered ip and mac is valid
    def check_valid_ip(self):
        status = subprocess.getstatusoutput("arp -a " + self.ip_address_stringvar.get())

        if self.ip_address_stringvar.get() == "":
            self.program_status_text_changer("Error in ip", "Ip field is invalid!","#d2e331")
            return False
        if "No" in status[1]:
            self.program_status_text_changer("Error in ip", "Check internet connection...","#d2e331")
            return False
        elif status[0] != 0:
            self.program_status_text_changer("Error in ip", "Ip field is invalid!","#d2e331")
            return False
        else:
            return True

    def show_help_frame(self, event):
        event.tkraise()

    def show_about_frame(self, event):
        event.tkraise()

    def back_to_main(self,event):
        event.tkraise()
    

    #enable the entry the boxes
    def enable_entries(self):
        self.path_entry.config(state='normal')
        self.ip_address_entry.config(state='normal')
        self.mac_address_entry.config(state='normal')

    #enable the disable the boxes
    def disable_entries(self):       
        self.path_entry.config(state='disabled')
        self.ip_address_entry.config(state='disabled')
        self.mac_address_entry.config(state='disabled')
    
    #disable the buttons
    def disable_buttons(self):
        self.test_button['state'] = 'disabled'
        self.start_button['state'] = 'disabled'
        self.select_path_button['state'] ='disabled'
    
    #enable the buttons
    def enable_buttons(self):
        self.test_button['state'] = 'normal'
        self.start_button['state'] = 'normal'
        self.select_path_button['state'] ='normal'

    #change program messages
    def program_status_text_changer(self, program_state_txt, arp_msg_lbl_txt, txt_color='red'):
        self.program_state.configure(text=program_state_txt, fg=txt_color)
        self.arp_message_label.configure(text=arp_msg_lbl_txt, fg=txt_color)
    
    #file dialog to get audiopath assigned to audio path button
    def get_audio_path(self):

        #if user changes the path of audio then stop the current music
        mixer.music.stop()
        self.is_test_alert = False

        files_ext = [('MP3 file', '*.mp3'),('WAV file', '*.wav')] 
        filename = askopenfilename(initialdir="/", filetypes=files_ext, defaultextension= files_ext)
        
        #clear entry before inserting new data
        self.path_entry.delete(0, END)
        self.path_entry.insert(0, filename)



    #test if alert audio is working
    def test_alert(self):

        if not self.is_test_alert:

            try:
                mixer.music.load(self.audio_path_stringvar.get())

                #-1 is used to loop indefinetly
                mixer.music.play(-1)
            except:
                self.program_status_text_changer("AUDIO PATH NOT VALID...", "Use mp3 or wav files", '#d2e331')
                return;
            

            #disable all other buttons if test button pressed
            self.stop_button['state'] = 'disabled'
            self.start_button['state'] = 'disabled'
            self.select_path_button['state'] ='disabled'
            self.disable_entries()

        
            #Show testing state
            self.program_status_text_changer("THIS IS A TEST...", "TEST: ARP SPOOFING DETECTED!","red")
            self.test_button.config(text="Stop Alert Test")
            self.is_test_alert = True

        else:
            self.start_button['state'] = 'normal'
            self.select_path_button['state'] ='normal'
            self.enable_entries()

            #Show testing state
            self.program_status_text_changer("STOPPED...", "TESTING STOPPED...", '#d2e331')

            self.test_button.config(text="Start Alert Test")
            mixer.music.stop()  
            self.is_test_alert = False

    
    #start the spoof detection process
    def start_arp_detector(self):

        if(self.check_valid_ip()):
            self.stop_button['state'] = 'normal'
            self.disable_buttons()
            self.disable_entries()

            #boolean to control start and stop program
            self.is_program_stopped = False
            self.start_process()

          
    def start_process(self):

        def run():
            self.program_state.configure(text="RUNNING...", fg="green")
            counter = 0
            check_interval = 11

            while not self.is_program_stopped:
                counter += 1

                subprocess.call("arp -a " + self.ip_address_stringvar.get())  
                arp_output = subprocess.getoutput("arp -a " + self.ip_address_stringvar.get())
                output_file = open("arp_call.txt", "w")
                output_file.write(arp_output+"\n")
                output_file.close()
                with open("arp_call.txt", "r") as file:                     
                        contents = file.read().split()
                        
                        if self.mac_address_stringvar.get() in contents:
                            self.arp_message_label.config(text="NO ARP SPOOFING DETECTED " + "Times Checked: " + str(counter), fg='green')
                    
                        else:
                            try:
                                self.program_status_text_changer("PRESS STOP BUTTON TO STOP MUSIC...","ARP SPOOFING DETECTED!","red")
                                mixer.music.load(self.audio_path_stringvar.get())

                                #-1 is used to loop indefinetly
                                mixer.music.play(-1)
                            except:
                               self.stop_button['state'] = 'disabled'
                               self.enable_buttons()
                               self.enable_entries()   
                               self.program_status_text_changer("AUDIO PATH NOT VALID","Use mp3 or wav files","#d2e331")   
                                                                                 
                            finally:
                               self.is_program_stopped = True
                               with open("spoof_info_save.txt", "a") as file:
                                  file.write(arp_output + "\n")
                    
                #if not interrupted then sleep for specfied number of seconds
                for i in range(check_interval):
                    if self.is_program_stopped:
                        break               
                    time.sleep(1)
            
        self.arp_process_thread = threading.Thread(target=run)
        self.arp_process_thread.start()

    #stop the program
    def stop_arp_detector(self):
        self.stop_button['state'] = 'disabled'
        self.enable_buttons()
        self.enable_entries()

        self.is_program_stopped = True
        self.program_state.configure(text="STOPPED...", fg='#d2e331')
        mixer.music.stop()  

    #handle stuff when user clicks on X out button to close app
    def on_closing(self):
        self.save_data()
        self.stop_arp_detector()
        root.destroy()
    
root = Tk()
win = Window(root)
root.protocol("WM_DELETE_WINDOW", win.on_closing)
root.mainloop()
