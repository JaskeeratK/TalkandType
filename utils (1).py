import sys
sys.modules["torch.__path__._path"] = None
import whisper
from pydub import AudioSegment
import language_tool_python
import difflib
from difflib import SequenceMatcher
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from sentence_transformers import SentenceTransformer,util
import textstat


def transcribed_audio(audio_path,model_size='tiny'):
    model=whisper.load_model(model_size)
    result=model.transcribe(audio_path)
    return result['text']

def calculate_fluency(audio_path,transcribed_text):
    audio=AudioSegment.from_file(audio_path)
    duration=len(audio)/1000
    wrd_cnt=len(transcribed_text.split())
    return round((wrd_cnt/duration)*60,2)

def check_grammar(text):
    url = "https://api.languagetool.org/v2/check"
    params = {
        "text": text,
        "language": "en-US"
    }
    response = requests.post(url, data=params)
    return response.json()

def correct_text(text,matches):
    corrected=text
    offset_shift=0
    for match in matches:
        replacement=match["replacements"][0]["value"] if match['replacements'] else ''
        start=match['offset']+offset_shift
        end=start+match['length']
        corrected=corrected[:start]+replacement+corrected[end:]
        offset_shift+=len(replacement)-match['length']
    return corrected

def check_email_format(text):
    issues=[]
    if "Subject:" not in text:
        issues.append("Subject is missing")
    if not any(word.lower().startswith(greetings) for word in text.splitlines() for greetings in ['dear','respected']):
        issues.append("Missing greeting like 'Dear Sir/Madam'")
    if not any(word.lower() in text.lower() for word in ["thank you","regards","sincerely"]):
        issues.append("Missing a proper closing")
    lines = text.strip().split('\n')
    last_line = lines[-1].strip()

    if not (last_line and last_line[0].isupper() and last_line.replace(" ", "").isalpha()):
        issues.append("Missing or incomplete name at the end of the email.")
    return issues
model=SentenceTransformer('all-MiniLM-L6-v2')

def check_relevance(user_Answer,reference):
    user_embedding=model.encode(user_Answer,convert_to_tensor=True)
    ref_embedding=model.encode(reference,convert_to_tensor=True)
    similarity=util.pytorch_cos_sim(user_embedding,ref_embedding)
    return float(similarity[0][0])

def preprocess(text):
    text=re.sub(r'[^\w\s]','',text)
    return text.lower().split()

def compare_text(reference,spoken):
    ref_words=preprocess(reference)
    spoken_words=preprocess(spoken)
    matcher=SequenceMatcher(None,ref_words,spoken_words)
    missing=[]
    extra=[]
    for tag,i1,i2,j1,j2 in matcher.get_opcodes():
        if tag=='delete':
            missing.extend(ref_words[i1:i2])
        elif tag=='insert':
            extra.extend(spoken_words[j1:j2])
        elif tag=='replace':
            missing.extend(ref_words[i1:i2])
            extra.extend(spoken_words[j1:j2])
    return {
        "missing":missing,
        "extra":extra,
        "accuracy":round((len(ref_words)-len(missing))/len(ref_words)*100,2)
    }

def compare_description(user_text,actual_text):
    vectorizer=TfidfVectorizer().fit_transform([user_text,actual_text])
    vectors=vectorizer.toarray()
    similarity=cosine_similarity([vectors[0]],[vectors[1]])[0][0]
    return round(similarity*100,2)

def check_article_format(text):
    issues=[]
    lines=text.split("\n")
    lines=[line.strip() for line in lines if line.strip()]

    if len(lines)<3:
        issues.append("Too short to be a proper article")
    if(len(lines[0].split()))>10:
        issues.append("Title is too long or missing")
    paragraph=text.strip().split('\n\n')
    if len(paragraph)<3:
        issues.append("Article must contain atleast 3 paragraphs(introduction,body and conclusion)")
    conclusion_found=any(
        phrase in text.lower()
        for phrase in ["in conclusion","to conclude","to sum up","at the end","overall","in short","in a nutshell","in summary","finally","as a result","all in all","ultimately","taking everything in account","after all is said and done"]
    )
    if not conclusion_found:
        issues.append("Conslusion seems to be missing")
    return issues

def analyze_vocab(text):
    return {
        "Difficult words":textstat.difficult_words(text),
        "Lexicon Count":textstat.lexicon_count(text)
    }
def vocab_feedback(vocab):
    diff_words=vocab['Difficult words']
    lexicon_count=vocab['Lexicon Count']
    feedback=[]
    if diff_words <= 5:
        feedback.append("❌ Very limited use of advanced vocabulary. Try using more formal or specific words.")
    elif diff_words <= 15:
        feedback.append("⚠️ Basic vocabulary used. Consider adding more variety.")
    elif diff_words <= 25:
        feedback.append("✅ Moderately rich vocabulary — appropriate for formal writing.")
    else:
        feedback.append("✅ Excellent use of advanced vocabulary.")
    if lexicon_count < 40:
        feedback.append("❌ Too short — try to elaborate more on your points.")
    elif lexicon_count <= 60:
        feedback.append("⚠️ Slightly brief — consider expanding your response.")
    elif lexicon_count <= 90:
        feedback.append("✅ Good word count — well-developed message.")
    else:
        feedback.append("✅ Thorough and detailed. Shows strong effort.")

    return feedback
