import sys
sys.modules["torch.__path__._path"] = None
import torch
import streamlit as st 
import requests
import tempfile 
from utils import transcribed_audio,calculate_fluency,compare_text,compare_description,check_grammar,correct_text,check_email_format,check_relevance,check_article_format,analyze_vocab,vocab_feedback
import os
from pydub import AudioSegment,silence
from PIL import Image
from streamlit_option_menu import option_menu 

with st.sidebar:
    mode=option_menu(
        menu_title=None,
        options=["Home","Reading","Speaking","Writing"],
        # orientation="horizontal"
    )


st.title("📚 Welcome to Talk & Type!")

if mode=="Home":
    st.markdown("""
        This platform helps you practice and evaluate your **Speaking**, **Reading**, and **Writing** skills through interactive tests and automated feedback.

        ### 🧭 How It Works:

        - **📖 Reading Test**:  
          Read a short passage aloud, record your voice, and get feedback on fluency, and content similarity.

        - **🗣️ Speaking Test**:  
          Describe the given Image. Receive insights on your clarity, vocabulary use, and fluency.

        - **✍️ Writing Test**:  
          Write emails or articles based on prompts. Get automatic feedback on grammar, vocabulary richness, structure, and relevance.
        
        ### 🧠 What You’ll Get:
        - Real-time transcription of your speech
        - Vocabulary and grammar analysis
        - Format checks (for emails and articles)
        - Constructive feedback for improvement

        ---

        ### 🚀 Ready to Begin?
        Use the navigation bar above to select a test.
    """)


if mode=="Reading":
    st.markdown("### 📖 Select the topic you'd like to read:")

    reading_topics = {
        "Technology & Society": (
            "Technology has dramatically transformed the fabric of modern life, influencing how we live, work, learn, and interact with one another. "
            "Over the past few decades, devices such as smartphones, personal computers, and the internet have become integral to our daily routines, reshaping communication, entertainment, and productivity. "
            "Social media platforms enable instant connection across the globe, while advancements in artificial intelligence and automation are redefining industries. "
            "However, this rapid evolution also raises concerns about privacy, digital addiction, job displacement, and the ethical use of technology. "
            "As we embrace innovation, it's essential to find a balance that ensures technology serves humanity positively and equitably."
        ),
        "Health & Lifestyle": (
            "Maintaining a healthy lifestyle involves more than just avoiding illness—it requires a holistic approach to physical, mental, and emotional well-being. "
            "A balanced diet rich in nutrients, regular physical activity, and adequate sleep are foundational elements. "
            "Equally important are stress management, mental health awareness, and hydration. "
            "In today’s fast-paced world, self-care practices such as mindfulness, relaxation techniques, and social connection are vital. "
            "Preventative healthcare, routine check-ups, and informed lifestyle choices help individuals lead longer, more fulfilling lives. "
            "Embracing a healthy lifestyle not only improves quality of life but also reduces the risk of chronic diseases and enhances productivity."
        ),
        "Environment": (
            "The environment is facing unprecedented challenges due to human activity, most notably climate change, deforestation, pollution, and biodiversity loss. "
            "Greenhouse gas emissions from industries, vehicles, and deforestation contribute to rising global temperatures, leading to more frequent natural disasters, melting polar ice, and rising sea levels. "
            "Protecting the environment requires coordinated action by individuals, communities, businesses, and governments. "
            "Practices such as recycling, conservation, sustainable farming, and transitioning to renewable energy sources are crucial. "
            "Educating the public about environmental issues and encouraging responsible consumption can help preserve the planet for future generations."
        ),
        "Education": (
            "Education is a powerful tool that enables individuals to unlock their potential and contribute meaningfully to society. "
            "It fosters critical thinking, creativity, empathy, and the ability to solve complex problems. "
            "Access to quality education can break cycles of poverty and inequality, opening doors to better employment opportunities and improved living standards. "
            "Beyond academic achievement, education plays a vital role in shaping values, promoting civic responsibility, and nurturing a global perspective. "
            "With advances in technology, education is becoming more accessible through online platforms and digital resources, allowing for lifelong learning and skill development in an ever-changing world."
        ),
        "Travel & Culture": (
            "Travel offers a unique opportunity to explore new places, experience different ways of life, and develop a deeper understanding of the world. "
            "By engaging with diverse cultures, languages, and traditions, travelers can gain fresh perspectives, challenge stereotypes, and foster empathy. "
            "Cultural exchange promotes mutual respect and global awareness, which are essential in an increasingly interconnected world. "
            "Whether it's tasting regional cuisine, participating in local festivals, or learning about historical landmarks, travel enriches the human experience. "
            "In addition to personal growth, sustainable tourism can also support local economies and preserve cultural heritage."
        ),
        "Science & Innovation": (
            "Science and innovation are the engines of progress, responsible for countless breakthroughs that have improved human life. "
            "From medical discoveries that save lives to technological advancements that increase efficiency and convenience, scientific research has a profound impact on society. "
            "Encouraging a spirit of curiosity, experimentation, and critical thinking is essential for continued advancement. "
            "Investment in science education, research infrastructure, and interdisciplinary collaboration paves the way for new inventions and solutions to global challenges. "
            "As we look to the future, ethical considerations and inclusive innovation will be key to ensuring that the benefits of progress are shared by all."
        )
    }
    cols = st.columns(3)
    for i, (name, path) in enumerate(reading_topics.items()):
        with cols[i % 3]:
            if st.button(name):
                st.session_state["selected_reading_topic"] = name
    if "selected_reading_topic" in st.session_state:
        st.markdown("### Please read the passage below:")
        selected_reading_topic=st.session_state["selected_reading_topic"]
        reference_text=reading_topics[selected_reading_topic]
        st.markdown(f"<div style='color:#000000;background-color:#f9f9f9;padding:10px;border-radius:10px'>{reference_text}</div>", unsafe_allow_html=True)


        audio_file=st.audio_input("Record yourself reading this")


        if audio_file:
    
            with tempfile.NamedTemporaryFile(delete=False,suffix=".wav") as tmp:
                tmp.write(audio_file.read())
                audio_path=tmp.name
            st.audio(audio_path,format="audio/wav")
            audio=AudioSegment.from_file(audio_path)
            duration_sec=len(audio)/1000.0
            if duration_sec<15:
                st.error("The file is too short. Please record at least 10 seconds of audio.")
            else:
                st.success("Audio file is acceptable!")

                transcript=transcribed_audio(audio_path)
                fluency_score=calculate_fluency(audio_path,transcript)
                similarity=compare_text(reference_text,transcript)

                st.markdown("## 📝Transcription:")
                st.write(transcript)

                st.markdown("## 📊Evaluation Metrics:")
    
                st.expander("🔍Similarity Evalution:")
                accuracy=similarity['accuracy']
                if accuracy>90:
                    st.markdown(f"**Accuracy:{accuracy}**")
                    st.success(f"{accuracy} ✅ Excellect! Very accurate reading")
                elif accuracy>75:
                    st.info(f"{accuracy}ℹ️ Good Job, just a few mistakes")
                else:
                    st.warning(f"{accuracy} ⚠️ Needs improvement,try reading more carefully")
                if similarity['missing']:
                    st.markdown("**❌Missing Words:**")
                    st.write(", ".join(similarity['missing']))
                if similarity['extra']:
                    st.markdown("**➕Extra Words:**")
                    st.write(", ".join(similarity['extra']))

    
            
                silences=silence.detect_silence(audio,min_silence_len=500,silence_thresh=-40)
                long_silences = [s for s in silences if s[1] - s[0] >= 2000]
                fillers=['uh','um','hmm','mm']
                filler_count=sum(transcript.lower().count(f) for f in fillers)
    
                st.markdown("## ⏸️Pauses and Hesitation Analysis:")
                st.markdown(f"**⏱️Number of long pauses:** {len(long_silences)}")
                st.markdown(f"**🗣️Filler words detected:** {filler_count}")
    
                word_cnt=len(transcript.split())
                if word_cnt<5:
                    st.warning("⚠️Very short or empty response detected.Please try re-reading")
                elif len(long_silences)>5:
                    st.warning("⚠️You had quite a few long pauses. Try to read more smoothly without frequent stops.")
                elif filler_count > 5:
                    st.warning("⚠️Frequent use of filler words detected. Practice reading clearly and confidently.")
                else:
                    st.success("✅Great job! You maintained a steady pace throughout")

    

                st.markdown("## 📊Fluency Score")
                if(0<=fluency_score<=80):
                    st.warning(f"Fluency Score: {fluency_score} WPM \n🔴LOW \nTry to read a bit more smoothly and confidently.")
    
                elif(81<=fluency_score<=120):
                    st.info(f"Fluency Score: {fluency_score} WPM \n🟠AVERAGE \nYou're doing okay — keep practicing to build more fluency.")
        
                elif(121<=fluency_score<=160):
                    st.success(f"Fluency Score: {fluency_score} WPM \n🟢GOOD \nNice pacing! That’s a comfortable and natural speed.")
    
                else:
                    st.success(f"Fluency Score: {fluency_score} WPM \n🟣VERY FAST \nYou're reading quite fast! Make sure clarity is not lost")

elif mode=="Speaking":
    st.markdown("### 🗣️ Select an Image to describe")
    image_options={
        "Image 1":"G:/python/reading_speaking/img1.png",
        "Image 2":"G:/python/reading_speaking/img2.png",
        "Image 3":"G:/python/reading_speaking/img3.png",
        "Image 4":"G:/python/reading_speaking/img4.png",
        "Image 5":"G:/python/reading_speaking/img5.png"
    }
    image_descriptions = {
    "Image 1": (
        "This map illustrates the percentage of individuals who never accessed the internet in 2021 "
        "across Europe, based on data from Eurostat. The UK data is from 2020. Colors indicate the "
        "percentage of non-internet users: yellow regions (0-4%), light green (4-8%), green (8-12%), "
        "dark green (12-16%), teal (16-21%), and purple (21-32%). Countries like Norway, Switzerland, "
        "and the Netherlands show the lowest percentages, while higher non-usage rates appear in parts "
        "of Eastern Europe and the Balkans. Several countries lack data, depicted in gray."
    ),
    "Image 2": (
        "This infographic details military spending by various countries, using different-sized circles "
        "to visually represent each country's military expenditure. The United States leads with $596 "
        "billion, significantly more than any other nation, and is considering a proposed increase of "
        "$54 billion. The next seven countries combined (including China with $215 billion, Saudi Arabia "
        "with $87 billion, Russia with $66 billion, Britain with $55 billion, India and France each with "
        "$51 billion, and Japan with $41 billion) spend $567 billion, nearly matching the U.S. total. All "
        "other countries combined spend $514 billion."
    ),
    "Image 3": (
        "The bar chart illustrates global pet food sales from 2010 to 2023, expressed in billions of U.S. "
        "dollars. The sales have shown an overall increasing trend over the years. Starting at $59.3 billion "
        "in 2010, there's a steady growth, with a slight dip in 2016 and 2017. The sales rebound and grow "
        "at an even faster rate, peaking at $133.9 billion in 2023. Over the span of just 13 years, sales "
        "of pet food have more than doubled globally."
    ),
    "Image 4": (
        "This bar chart displays Europe's top ten coffee-drinking nations based on cups of coffee consumed "
        "per capita in 2015. In general, coffee consumption varies significantly between the countries. "
        "Finland leads significantly with 1,310 cups per person, followed by Sweden at 1,070, and the "
        "Netherlands with 1,004 cups. Denmark and Germany consume 863 and 675 cups respectively, showing "
        "moderate consumption. Italy, known for its coffee culture, surprisingly consumed just 658 cups. "
        "Estonia, Austria, France, and Portugal also make the list, each consuming between 482 and 635 cups per capita."
    ),
    "Image 5": (
        "This pie chart displays the most-owned laptop brands in South Africa as of June 2023, based on a "
        "MyBroadband poll. Dell leads with 22.7% ownership, followed closely by HP at 19.5%. Lenovo holds "
        "17.6%, and Apple has 14.3%. Asus and Acer have smaller shares at 9.2% and 6.8% respectively. The "
        "category labeled 'Other' accounts for 9.9% of laptop ownership. Overall, the data indicates that "
        "there is not one dominant laptop brand in South Africa."
    ),
}

    cols = st.columns(3)
    for i, (name, path) in enumerate(image_options.items()):
        with cols[i % 3]:
            if st.button(name):
                st.session_state["selected_image"] = path
                st.session_state["selected_image_name"]= name
    if "selected_image" in st.session_state:
        selected_name=st.session_state["selected_image_name"]
        selected_path=st.session_state["selected_image"]
        st.markdown("### 🖼️ Selected Image:")
        st.image(selected_path, caption=selected_name, use_container_width=True)
        audio_file=st.audio_input("Record yourself describing this Image(80-100 words)")


        if audio_file:
    
            with tempfile.NamedTemporaryFile(delete=False,suffix=".wav") as tmp:
                tmp.write(audio_file.read())
                audio_path=tmp.name
            st.audio(audio_path,format="audio/wav")

            reference_text=image_descriptions[selected_name]
            transcript=transcribed_audio(audio_path)
            fluency_score=calculate_fluency(audio_path,transcript)
            similarity=compare_description(transcript,reference_text)

            grammar=check_grammar(transcript)
            matches=grammar.get("matches",[])
            corrected=correct_text(transcript,matches)

            vocab=analyze_vocab(transcript)
            vocab_feedback=vocab_feedback(vocab)

            audio=AudioSegment.from_file(audio_path)
            duration_sec=len(audio)/1000.0
            if duration_sec<15:
                st.error("The file is too short. Please record at least 10 seconds of audio.")
            else:
                st.success("Audio file is acceptable!")
                st.markdown("## 📝Transcription:")
                st.write(transcript)
                st.markdown("## Your Answer should look like:")
                st.write(reference_text)

                st.markdown("## 📊Evaluation Metrics:")
                relevance=check_relevance(transcript,reference_text)
                st.markdown(f"**🔍 Similarity Score:** {relevance*100:.2f}%")
                if relevance*100 > 70:
                    st.success("✅ Excellent description! Very close to the expected answer.")
                elif relevance*100 > 40:
                    st.info("🟡 Good effort, but try to include more detail.")
                else:
                    st.warning("🔴 Try to describe more clearly and completely.")


                silences=silence.detect_silence(audio,min_silence_len=500,silence_thresh=-40)
                long_silences = [s for s in silences if s[1] - s[0] >= 2000]
                fillers=['uh','um','hmm','mm']
                filler_count=sum(transcript.lower().count(f) for f in fillers)
    
                st.markdown("## ⏸️Pauses and Hesitation Analysis:")
                st.markdown(f"**⏱️Number of long pauses:** {len(long_silences)}")
                st.markdown(f"**🗣️Filler words detected:** {filler_count}")
    
                word_cnt=len(transcript.split())
                if word_cnt<5:
                    st.warning("⚠️Very short or empty response detected.Please try re-reading")
                elif len(long_silences)>5:
                    st.warning("⚠️You had quite a few long pauses. Try to read more smoothly without frequent stops.")
                elif filler_count > 5:
                    st.warning("⚠️Frequent use of filler words detected. Practice reading clearly and confidently.")
                else:
                    st.info("✅Great job! You maintained a steady pace throughout")
                
                st.markdown("## Vocabulary:")
                for line in vocab_feedback:
                    st.write(line)

                st.markdown("## Grammatical Analysis:")
                st.write(corrected)

                
                if matches:
                    st.markdown("### ⚠️ Issues Found")
                    for match in matches:
                        message = match.get("message", "Unknown issue")
                        replacements = match.get("replacements", [])
                        suggestion = replacements[0]["value"] if replacements else "No suggestion"
                        st.markdown(f"- **{message}** → Suggested: `{suggestion}`")
                else:
                    st.success("No grammar issues detected!")

                st.markdown("## 📊Fluency Score")
                if(0<=fluency_score<=80):
                    st.warning(f"Fluency Score: {fluency_score} WPM \n🔴LOW \nTry to speak a bit more smoothly and confidently.")

                elif(81<=fluency_score<=120):
                    st.info(f"Fluency Score: {fluency_score} WPM \n🟠AVERAGE \nYou're doing okay — keep practicing to build more fluency.")
    
                elif(121<=fluency_score<=160):
                    st.success(f"Fluency Score: {fluency_score} WPM \n🟢GOOD \nNice pacing! That’s a comfortable and natural speed.")

                else:
                    st.success(f"Fluency Score: {fluency_score} WPM \n🟣VERY FAST \nYou're speaking quite fast! Make sure clarity is not lost")
elif mode=="Writing":
    st.markdown("### 📖 Would you like to write an email or do you prefer an article to write?")
    test_type=st.radio("Select one",["--select a test--","Email","Article"],horizontal=True)
    if test_type=="Email":
        st.markdown("## Select a topic to write an Email:")
        email_topics = {
            "topic1": {
                "title": "Request for Leave",
                "prompt": (
                    "You are unwell and need to take a 3-day leave from school/college. "
                    "Write an email to your class teacher explaining your situation and requesting leave."
                ),
                "reference": (
                    "Subject: Request for Sick Leave\n\n"
                    "Dear Sir/Madam,\n\n"
                    "I am writing to inform you that I have been unwell for the past day and was diagnosed with the flu. "
                    "My doctor has advised complete rest for the next three days. Therefore, I kindly request you to grant me leave from "
                    "June 5th to June 7th. I will catch up with all the missed work and notes upon my return.\n\n"
                    "Thank you for your understanding.\n\n"
                    "Sincerely,\n"
                    "Your Name"
                )
            },
            "topic2": {
                "title": "Follow-up on Assignment Submission",
                "prompt": (
                    "You submitted an assignment last week but haven't received any feedback. "
                    "Write an email to your professor politely asking for an update."
                ),
                "reference": (
                    "Subject: Request for Feedback on Submitted Assignment\n\n"
                    "Dear Professor,\n\n"
                    "I hope you are doing well. I am writing to follow up on the assignment I submitted on May 28th for the Data Structures course. "
                    "I understand that you have a busy schedule, but I would be grateful if you could provide any feedback or let me know when it might be reviewed.\n\n"
                    "Thank you for your time and support.\n\n"
                    "Warm regards,\n"
                    "Your Name"
                ),
            },
            "topic3": {
                "title": "Request for Library Access",
                "prompt": (
                    "You need access to a restricted section of the college library for research. "
                    "Write an email to the librarian requesting permission."
                ),
                "reference": (
                    "Subject: Request for Access to Restricted Library Section\n\n"
                    "Dear Librarian,\n\n"
                    "I am a third-year student currently working on my final year research project related to historical manuscripts. "
                    "I understand that some of the resources I need are available in the restricted section of the library. "
                    "Please let me know if any formal procedure or written consent is required.\n\n"
                    "Thank you for your assistance.\n\n"
                    "Sincerely,\n"
                    "Your Name"
                )
            },
            "topic4": {
                "title": "Complaint about a Classroom Issue",
                "prompt": (
                    "There is consistent noise disruption during your lectures from nearby construction. "
                    "Write an email to the academic coordinator requesting action."
                ),
                "reference": (
                    "Subject: Noise Disruption During Lectures\n\n"
                    "Dear Academic Coordinator,\n\n"
                    "I hope this message finds you well. I would like to bring to your attention an issue affecting our classroom environment. "
                    "Due to ongoing construction work near the C-Block, our lectures are frequently disturbed by loud noises, making it difficult to focus and hear the instructor.\n\n"
                    "I kindly request you to look into this matter and consider shifting our classes to a quieter location until the construction is complete.\n\n"
                    "Thank you for your support.\n\n"
                    "Sincerely,\n"
                    "Your Name"
                )
            },
            "topic5": {
                "title": "Application for a Workshop",
                "prompt": (
                    "You want to attend a technical workshop organized by your college. "
                    "Write an email to the coordinator requesting registration and asking for more details."
                ),
                "reference": (
                    "Subject: Request for Workshop Registration and Details\n\n"
                    "Dear Workshop Coordinator,\n\n"
                    "I am writing to express my interest in attending the upcoming workshop on Machine Learning scheduled for next week. "
                    "I would like to request registration for the event and would also appreciate if you could share the agenda and any prerequisites for participation.\n\n"
                    "Looking forward to your response.\n\n"
                    "Regards,\n"
                    "Your Name"
                )
            }
        }
        cols=st.columns(len(email_topics))
        for i ,(key,topic) in enumerate(email_topics.items()):
            with cols[i]:
                if st.button(topic["title"]):
                    st.session_state["selected_topic"]=key

        if "selected_topic" in st.session_state:
            selected=email_topics[st.session_state["selected_topic"]]
            st.markdown(f"### 📨 Topic: **{selected['title']}**")
            st.markdown(f"**Prompt:** {selected['prompt']}")
            user_input = st.text_area("✍️ Write your email here:", height=300) or ""

            if st.button("✅ Submit Response"):
                if user_input.strip():
                    selected_key = st.session_state["selected_topic"]
                    reference_text = email_topics[selected_key]["reference"]
                    st.success("Your response has been submitted!")

                    lines = user_input.strip().split('\n')
                    text_for_grammar = "\n".join(lines[:-1]) if len(lines) > 1 else user_input
                    grammar=check_grammar(text_for_grammar)
                    matches=grammar.get("matches",[])
                    corrected=correct_text(user_input,matches)

                    email_format=check_email_format(user_input)

                    vocab=analyze_vocab(user_input)
                    vocab_feedback=vocab_feedback(vocab)

                    relevance=check_relevance(user_input,reference_text)

                    st.markdown("## Format Check:")
                    if not email_format:
                        st.success("✅ Format Check Passed: No format issues found.")
                    else:
                        st.error("❌ Format Issues Found:")
                        for issue in email_format:
                            st.markdown(f"-{issue}")
                    st.markdown("## Vocabulary:")
                    for line in vocab_feedback:
                        st.write(line)

                    st.markdown("## Grammar Analysis")
                    st.write(corrected)
                    if matches:
                        st.markdown("### ⚠️ Issues Found")
                        for match in matches:
                            message = match.get("message", "Unknown issue")
                            replacements = match.get("replacements", [])
                            suggestion = replacements[0]["value"] if replacements else "No suggestion"
                            st.markdown(f"- **{message}** → Suggested: `{suggestion}`")
                    st.markdown("## Similarity to the reference text")
                    if relevance*100 > 70:
                        st.success(f"🚀Great Job! Your article is very similar to the refernce text ,{relevance*100} score")
                    elif relevance*100 > 40:
                        st.success(f"🟡Average but you can do better with your writing skills , {relevance*100} score")
                    elif relevance*100 > 10:
                        st.success(f"🚫Poor job ,try writing more carefully according to the topic , {relevance*100} score")

            
                else:
                    st.warning("Please write your response before submitting.")
    elif test_type=="Article":
        article_topics = {
            "topic1": {
                "title": "The Importance of Mental Health Awareness",
                "content": (
                    "Mental health is as important as physical health, yet it is often neglected or misunderstood. "
                    "In today’s fast-paced world, anxiety, depression, and stress are becoming increasingly common, especially among young people.\n\n"
                    "Raising awareness about mental health helps reduce stigma and encourages people to seek help. Schools, workplaces, and families all play a vital role "
                    "in creating an environment where mental well-being is prioritized.\n\n"
                    "In conclusion, mental health is not a luxury but a necessity. A healthy mind leads to a productive and happy life. It’s time we talk openly and support one another."
                )
            },
            "topic2": {
                "title": "The Role of Technology in Education",
                "content": (
                    "Technology has transformed education in the 21st century. From smart classrooms to online courses, it has made learning more interactive and accessible.\n\n"
                    "Students can now attend virtual lectures, use educational apps, and access resources from across the globe. Teachers also benefit from tools that allow personalized learning.\n\n"
                    "While challenges like screen fatigue and digital divide exist, the overall impact of technology in education has been positive. It prepares students for a tech-driven world."
                )
            },
            "topic3": {
                "title": "Climate Change and Its Global Impact",
                "content": (
                    "Climate change is one of the most pressing issues facing the world today. Rising temperatures, melting glaciers, and extreme weather events are evidence of its growing impact.\n\n"
                    "Human activities such as deforestation and excessive fossil fuel use are major contributors. These lead to rising sea levels, loss of biodiversity, and threats to food security.\n\n"
                    "We must act now—by adopting renewable energy, conserving forests, and reducing emissions. Every small step counts toward saving our planet."
                )
            },
            "topic4": {
                "title": "Should Homework Be Banned?",
                "content": (
                    "Homework has always been a part of school life, but its relevance is often debated. While it reinforces classroom learning, it can also cause stress and limit time for extracurriculars.\n\n"
                    "Some argue that quality is more important than quantity. Instead of excessive assignments, meaningful and manageable tasks should be given.\n\n"
                    "Rather than banning homework entirely, educators should focus on making it more balanced and engaging."
                )
            },
            "topic5": {
                "title": "The Power of Reading Books",
                "content": (
                    "Reading books is a powerful habit that enriches our minds and lives. It enhances vocabulary, improves focus, and sparks imagination.\n\n"
                    "Unlike digital content, books offer a deep and immersive experience. They encourage critical thinking and empathy by letting us see the world through different perspectives.\n\n"
                    "In an age of short attention spans, reading is a timeless treasure. Everyone should cultivate the habit of reading daily."
                )
            }
        }
        st.markdown("## Select a topic to write an Article:")
        cols=st.columns(len(article_topics))
        for i ,(key,topic) in enumerate(article_topics.items()):
            with cols[i]:
                if st.button(topic["title"]):
                    st.session_state["selected_article_topic"]=key

        if "selected_article_topic" in st.session_state:
            selected=article_topics[st.session_state["selected_article_topic"]]
            st.markdown(f"### 📨 Topic: **{selected['title']}**")
            user_input = st.text_area("✍️ Write your article here:", height=300) or ""
            if st.button("✅ Submit Response"):
                if user_input.strip():
                    selected_key = st.session_state["selected_article_topic"]
                    reference_text = article_topics[selected_key]["content"]
                    st.success("Your response has been submitted!")
                    
                    grammar=check_grammar(user_input)
                    matches=grammar.get("matches",[])
                    corrected=correct_text(user_input,matches)

                    article_format=check_article_format(user_input)

                    vocab=analyze_vocab(user_input)
                    vocab_feedback=vocab_feedback(vocab)
                    
                    relevance=check_relevance(user_input,reference_text)

                    st.markdown("## Format Check:")
                    if not article_format:
                        st.success("✅ Format Check Passed: No format issues found.")
                    else:
                        st.error("❌ Format Issues Found:")
                        for issue in article_format:
                            st.markdown(f"-{issue}")

                    st.markdown("## Vocabulary")
                    for line in vocab_feedback:
                        st.write(line)

                    st.markdown("## Grammar Analysis")
                    st.write(corrected)

                    if matches:
                        st.markdown("### ⚠️ Issues Found")
                        for match in matches:
                            message = match.get("message", "Unknown issue")
                            replacements = match.get("replacements", [])
                            suggestion = replacements[0]["value"] if replacements else "No suggestion"
                            st.markdown(f"- **{message}** → Suggested: `{suggestion}`")
                    st.markdown("## Similarity to the reference text")
                    if relevance*100 > 70:
                        st.success(f"🚀Great Job! Your article is very similar to the refernce text ,{relevance*100} score")
                    elif relevance*100 > 40:
                        st.success(f"🟡Average but you can do better with your writing skills , {relevance*100} score")
                    elif relevance*100 > 10:
                        st.success(f"🚫Poor job ,try writing more carefully according to the topic , {relevance*100} score")


            
                else:
                    st.warning("Please write your response before submitting.")

    


else:
    st.write("Please select a test to proceed")
