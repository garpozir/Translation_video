#! /data/data/com.termux/files/usr/bin/python3
#garpozir@gmail.com

from pydub import AudioSegment
import time,itertools,threading,os,subprocess
import moviepy.editor as mp
import speech_recognition as sr
from os import system,name
from googletrans import Translator

def video_duration(input_video):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration=float(result.stdout)
    min_video=int(duration//60)
    sec_video=int(duration%60)
    if sec_video==0:
        sec_video=1
    return min_video,sec_video,int(duration)

def extract_audio(video_file):
    print('در حال جدا کردن صوت از ویدئو...\n')
    video_file=mp.VideoFileClip(video_file)
    video_file.audio.write_audiofile('audio_file.wav')

def wav_to_text(tm):
    time.sleep(0.5)
    done = False
    def animate():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            sys.stdout.write('\rدر حال تبدیل صوت به متن... '+tm + c)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r\n     ')
    t = threading.Thread(target=animate)
    t.start()
    AUDIO_FILE = 'audio_file.wav'
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    finally:
        done=True

def Translation(text):
    time.sleep(1)
    print('\nدر حال ترجمه متن...')
    g=Translator()
    trans=g.translate(text, 'fa')
    trans=trans.text
    return trans

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    trim_ms=0
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
        trim_ms+=chunk_size
    return trim_ms

def subtitle(trans,len_trans,start_trim,end_trim,video_time,file_name):
    print('\nدر حال ساخت زیرنویس...\n')
    file_name=file_name.split('/')[-1]
    file_name=file_name.split('.')[0]+'.srt'
    video_time=video_time-start_trim-end_trim
    lop=len_trans//50
    if len_trans%50!=0:
        lop+=1
    show_sub=video_time/lop
    num=0
    s_min=0
    e_min=0
    with open(file_name,'w',encoding='utf-8')as f:
        if start_trim>59:
            start_trim=59
        for i in range(1,lop+1):
            try:
                char=(50*i)+1
                final_txt=trans[num:char-1]
                noe=True
                while ord(trans[char]) not in (32,44,46):
                    char+=1
                    final_txt=trans[num:char]
                    noe=False
                if noe==True:
                    num=50*i
                else:
                    num=char
            except IndexError:
                final_txt=trans[num:]
            end_trim=start_trim+show_sub
            if end_trim>59:
                end_trim-=60
                e_min+=1
            end_trim=round(end_trim,3)
            start_trim=round(start_trim,3)
            e_min=round(e_min,3)
            s_min=round(s_min,3)
            if start_trim<10:
                istart_trim='0'+str(start_trim)
            else:
                istart_trim=str(start_trim)
            if end_trim < 10:
                iend_trim='0'+str(end_trim)
            else:
                iend_trim=str(end_trim)
            if s_min < 10:
                is_min='0'+str(s_min)
            else:
                is_min=+str(s_min)
            if e_min < 10:
                ie_min='0'+str(e_min)
            else:
                ie_min=+str(e_min)
            istart_trim=istart_trim.split('.')
            istart_trim=','.join(istart_trim)
            iend_trim=iend_trim.split('.')
            iend_trim=','.join(iend_trim)
            if istart_trim.find(',')==-1:
                istart_trim+=',011'
            if iend_trim.find(',')==-1:
                iend_trim+=',010'
            istart_trim=istart_trim.split(',')
            if len(istart_trim[1])!=3:
                istart_trim[1]=istart_trim[1].zfill(3)
            istart_trim=','.join(istart_trim)
            iend_trim=iend_trim.split(',')
            if len(iend_trim[1])!=3:
                iend_trim[1]=iend_trim[1].zfill(3)
            iend_trim=','.join(iend_trim)
            f.write(f'{i}\n00:{is_min}:{istart_trim} --> 00:{ie_min}:{iend_trim}\n{final_txt}\n\n')
            start_trim+=show_sub
            if start_trim>59:
                start_trim-=60
                s_min+=1
    f.close()

if name == 'nt':
     _ = system('cls')
else:
    _ = system('clear')

def main():
    def del_():
        if os.path.isfile('audio_file.wav'):
            os.remove('audio_file.wav')
    try:
        video_time=video_duration(sys.argv[1])
        if video_time[2]>260:
            print('در نسخه رایگان نرم افزار حداکثر میتوانید 4 دقیقه ویدئو آپلود کنید')
            return 0
        tm=int((video_time[2]*70)/100)
        if tm < 61:
            tm='کمتر از 1 دقیقه'
        else:
            tm='کمتر از '+str((tm//60)+1)+' دقیقه '
        extract_audio(sys.argv[1])
        english_text=wav_to_text(tm)
        trans=Translation(english_text)
        len_trans=len(trans)
        sound=AudioSegment.from_file('audio_file.wav', format="wav")
        start_trim=(detect_leading_silence(sound))//1000
        end_trim=(detect_leading_silence(sound.reverse()))//1000
        del english_text
        del_()
        subtitle(trans,len_trans,start_trim,end_trim,video_time[2],sys.argv[1])
        print('***انجام شد (:***')
    except IndexError:
        del_()
        sys.exit('نام و آدرس ویدئو را وارد نکرده اید\nexam: python main.py movie.mp4')
    except:
        del_()
        sys.exit('خطا\nشاید فرمت ویدئو مناسب نیست')

if __name__=='__main__':
    import sys
    main()
