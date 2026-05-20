# import streamlit as st
# import PIL.Image
# import os
# import tempfile
# import uuid

# # --- THE FIX: Monkey Patch for Pillow 10+ ---
# if not hasattr(PIL.Image, 'ANTIALIAS'):
#     PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
# # ---------------------------------------------

# from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, ImageClip
# import moviepy.video.fx.all as vfx

# st.set_page_config(page_title="Batch News Broadcaster", layout="wide")

# # --- INITIALIZE SESSION STATE (THE QUEUE MEMORY) ---
# if 'job_queue' not in st.session_state:
#     st.session_state.job_queue = []
# if 'is_processing' not in st.session_state:
#     st.session_state.is_processing = False

# st.title("📺 Batch News Broadcast Generator")
# st.markdown("Upload pairs one by one to build your queue. Videos are cropped to fill the screen edge-to-edge.")

# # ==========================================
# # SECTION 1: ADD TO QUEUE
# # ==========================================
# st.subheader("1. Add a Pair to the Queue")

# with st.container(border=True):
#     col1, col2 = st.columns(2)
#     with col1:
#         vid1_file = st.file_uploader("Upload Anchor Video (Left)", type=['mp4', 'mov', 'avi'], key="anchor_up")
#     with col2:
#         vid2_file = st.file_uploader("Upload Event Video (Right)", type=['mp4', 'mov', 'avi'], key="event_up")

#     col3, col4 = st.columns(2)
#     with col3:
#         audio_choice = st.radio("Choose audio source:", ("Keep Anchor Audio", "Keep Event Audio", "Mix Both"), key="audio_up")
#     with col4:
#         logo_file = st.file_uploader("Upload Channel Logo (PNG)", type=['png'], key="logo_up")

#     job_name = st.text_input("Name this broadcast (e.g., 'Morning_Segment_1')")

#     if st.button("➕ Add Pair to Queue", type="primary"):
#         if vid1_file and vid2_file and job_name:
#             # Save files to disk immediately so they survive page refreshes
#             job_id = str(uuid.uuid4())[:8]
#             os.makedirs("temp_queue", exist_ok=True)
            
#             p1 = f"temp_queue/{job_id}_anchor.mp4"
#             p2 = f"temp_queue/{job_id}_event.mp4"
#             with open(p1, "wb") as f: f.write(vid1_file.read())
#             with open(p2, "wb") as f: f.write(vid2_file.read())
            
#             p_logo = None
#             if logo_file:
#                 p_logo = f"temp_queue/{job_id}_logo.png"
#                 with open(p_logo, "wb") as f: f.write(logo_file.read())

#             # Add to memory
#             st.session_state.job_queue.append({
#                 "id": job_id,
#                 "name": job_name,
#                 "anchor": p1,
#                 "event": p2,
#                 "logo": p_logo,
#                 "audio": audio_choice,
#                 "status": "Waiting",
#                 "output": None
#             })
#             st.success(f"Added '{job_name}' to queue!")
#             st.rerun() 
#         else:
#             st.error("Please upload both videos and give the job a name.")

# # ==========================================
# # SECTION 2: QUEUE DASHBOARD & PROCESSING
# # ==========================================
# st.divider()
# st.subheader(f"2. Processing Queue ({len(st.session_state.job_queue)} Items)")

# # Show the current queue
# for job in st.session_state.job_queue:
#     if job['status'] == "Waiting":
#         st.info(f"⏳ **Waiting:** {job['name']}")
#     elif job['status'] == "Processing":
#         st.warning(f"⚙️ **Processing right now:** {job['name']}")
#     elif job['status'] == "Done":
#         col_a, col_b = st.columns([3, 1])
#         with col_a:
#             st.success(f"✅ **Finished:** {job['name']}")
#         with col_b:
#             with open(job['output'], "rb") as f:
#                 st.download_button(label="⬇️ Download", data=f, file_name=f"{job['name']}.mp4", mime="video/mp4", key=f"dl_{job['id']}")

# # The Processing Trigger
# if len(st.session_state.job_queue) > 0:
#     waiting_jobs = [j for j in st.session_state.job_queue if j['status'] == "Waiting"]
    
#     if len(waiting_jobs) > 0 and not st.session_state.is_processing:
#         if st.button("🚀 Start Processing Queue"):
#             st.session_state.is_processing = True
#             st.rerun()

#     # THE ACTUAL PROCESSING LOOP
#     if st.session_state.is_processing:
#         for job in st.session_state.job_queue:
#             if job['status'] == "Waiting":
#                 job['status'] = "Processing"
                
#                 try:
#                     clip1 = VideoFileClip(job['anchor'])
#                     clip2 = VideoFileClip(job['event'])
                    
#                     # 1. Handle Duration Loop
#                     max_duration = max(clip1.duration, clip2.duration)
#                     if clip1.duration < max_duration: clip1 = clip1.fx(vfx.loop, duration=max_duration)
#                     if clip2.duration < max_duration: clip2 = clip2.fx(vfx.loop, duration=max_duration)

#                     # 2. Crop and Fill Logic (No Black Bars)
#                     def crop_and_fill(clip, target_w=960, target_h=1080):
#                         current_ratio = clip.w / clip.h
#                         target_ratio = target_w / target_h

#                         if current_ratio > target_ratio:
#                             # Too wide -> scale height perfectly, crop width from center
#                             clip = clip.resize(height=target_h)
#                             clip = clip.crop(x_center=clip.w/2, width=target_w)
#                         else:
#                             # Too tall -> scale width perfectly, crop height from center
#                             clip = clip.resize(width=target_w)
#                             clip = clip.crop(y_center=clip.h/2, height=target_h)
#                         return clip

#                     clip1 = crop_and_fill(clip1)
#                     clip2 = crop_and_fill(clip2)
                    
#                     # 3. Position Flush with Edges
#                     clip1 = clip1.set_position((0, 0))
#                     clip2 = clip2.set_position((960, 0))
                    
#                     # 4. Canvas & Layers
#                     canvas = ColorClip(size=(1920, 1080), color=(0,0,0), duration=max_duration)
#                     video_layers = [canvas, clip1, clip2]
                    
#                     if job['logo']:
#                         logo_clip = ImageClip(job['logo']).resize(height=100)
#                         # Position Top-Right over the video
#                         logo_clip = logo_clip.set_position((1920 - logo_clip.w - 50, 50)).set_duration(max_duration)
#                         video_layers.append(logo_clip)
                    
#                     # 5. Audio Handling
#                     final_audio = None
#                     if job['audio'] == "Keep Anchor Audio" and clip1.audio: final_audio = clip1.audio
#                     elif job['audio'] == "Keep Event Audio" and clip2.audio: final_audio = clip2.audio
#                     elif job['audio'] == "Mix Both" and clip1.audio and clip2.audio:
#                         from moviepy.audio.AudioClip import CompositeAudioClip
#                         final_audio = CompositeAudioClip([clip1.audio, clip2.audio])
#                     else:
#                         final_audio = clip1.audio or clip2.audio
                        
#                     final_video = CompositeVideoClip(video_layers)
#                     if final_audio: final_video = final_video.set_audio(final_audio)
                    
#                     os.makedirs("finished_renders", exist_ok=True)
#                     out_path = f"finished_renders/{job['name']}_{job['id']}.mp4"
                    
#                     # 6. RENDER
#                     final_video.write_videofile(out_path, codec="libx264", audio_codec="aac", preset="ultrafast")
                    
#                     job['output'] = out_path
#                     job['status'] = "Done"
                    
#                 finally:
#                     # CLEANUP TO SAVE RAM FOR THE NEXT VIDEO
#                     try: clip1.close() 
#                     except: pass
#                     try: clip2.close() 
#                     except: pass
#                     if job['logo']:
#                         try: logo_clip.close()
#                         except: pass
                    
#                     # Delete the temp inputs to save hard drive space
#                     if os.path.exists(job['anchor']): os.remove(job['anchor'])
#                     if os.path.exists(job['event']): os.remove(job['event'])
#                     if job['logo'] and os.path.exists(job['logo']): os.remove(job['logo'])
                
#                 # Refresh UI after each video finishes to show its download button
#                 st.rerun() 
        
#         st.session_state.is_processing = False
#         st.success("🎉 Entire queue is finished!")






import streamlit as st
import PIL.Image
import os
import tempfile
import uuid

# --- THE FIX: Monkey Patch for Pillow 10+ ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
# ---------------------------------------------

from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, ImageClip
import moviepy.video.fx.all as vfx

st.set_page_config(page_title="Batch News Broadcaster", layout="wide")

# --- INITIALIZE SESSION STATE (THE QUEUE MEMORY) ---
if 'job_queue' not in st.session_state:
    st.session_state.job_queue = []
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

st.title("📺 Batch News Broadcast Generator")
st.markdown("Upload pairs, trim durations, and process them sequentially to save computer memory.")

# ==========================================
# SECTION 1: ADD TO QUEUE
# ==========================================
st.subheader("1. Add a Pair to the Queue")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        vid1_file = st.file_uploader("Upload Anchor Video (Left)", type=['mp4', 'mov', 'avi'], key="anchor_up")
        col1a, col1b = st.columns(2)
        with col1a: a_start = st.text_input("Start Time (MM:SS)", value="00:00", key="a_start")
        with col1b: a_end = st.text_input("End Time (MM:SS)", value="", placeholder="Leave blank for full", key="a_end")

    with col2:
        vid2_file = st.file_uploader("Upload Event Video (Right)", type=['mp4', 'mov', 'avi'], key="event_up")
        col2a, col2b = st.columns(2)
        with col2a: e_start = st.text_input("Start Time (MM:SS)", value="00:00", key="e_start")
        with col2b: e_end = st.text_input("End Time (MM:SS)", value="", placeholder="Leave blank for full", key="e_end")

    st.divider()
    
    col3, col4 = st.columns(2)
    with col3:
        audio_choice = st.radio("Choose audio source:", ("Keep Anchor Audio", "Keep Event Audio", "Mix Both"), key="audio_up")
    with col4:
        logo_file = st.file_uploader("Upload Channel Logo (PNG)", type=['png'], key="logo_up")

    job_name = st.text_input("Name this broadcast (e.g., 'Morning_Segment_1')")

    if st.button("➕ Add Pair to Queue", type="primary"):
        if vid1_file and vid2_file and job_name:
            # Save files to disk immediately
            job_id = str(uuid.uuid4())[:8]
            os.makedirs("temp_queue", exist_ok=True)
            
            p1 = f"temp_queue/{job_id}_anchor.mp4"
            p2 = f"temp_queue/{job_id}_event.mp4"
            with open(p1, "wb") as f: f.write(vid1_file.read())
            with open(p2, "wb") as f: f.write(vid2_file.read())
            
            p_logo = None
            if logo_file:
                p_logo = f"temp_queue/{job_id}_logo.png"
                with open(p_logo, "wb") as f: f.write(logo_file.read())

            # Add to memory
            st.session_state.job_queue.append({
                "id": job_id,
                "name": job_name,
                "anchor": p1,
                "anchor_start": a_start,
                "anchor_end": a_end if a_end.strip() != "" else None,
                "event": p2,
                "event_start": e_start,
                "event_end": e_end if e_end.strip() != "" else None,
                "logo": p_logo,
                "audio": audio_choice,
                "status": "Waiting",
                "output": None
            })
            st.success(f"Added '{job_name}' to queue!")
            st.rerun() 
        else:
            st.error("Please upload both videos and give the job a name.")

# ==========================================
# SECTION 2: QUEUE DASHBOARD & PROCESSING
# ==========================================
st.divider()
st.subheader(f"2. Processing Queue ({len(st.session_state.job_queue)} Items)")

for job in st.session_state.job_queue:
    if job['status'] == "Waiting":
        st.info(f"⏳ **Waiting:** {job['name']}")
    elif job['status'] == "Processing":
        st.warning(f"⚙️ **Processing right now:** {job['name']}")
    elif job['status'] == "Done":
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.success(f"✅ **Finished:** {job['name']}")
        with col_b:
            with open(job['output'], "rb") as f:
                st.download_button(label="⬇️ Download", data=f, file_name=f"{job['name']}.mp4", mime="video/mp4", key=f"dl_{job['id']}")

if len(st.session_state.job_queue) > 0:
    waiting_jobs = [j for j in st.session_state.job_queue if j['status'] == "Waiting"]
    
    if len(waiting_jobs) > 0 and not st.session_state.is_processing:
        if st.button("🚀 Start Processing Queue"):
            st.session_state.is_processing = True
            st.rerun()

    if st.session_state.is_processing:
        for job in st.session_state.job_queue:
            if job['status'] == "Waiting":
                job['status'] = "Processing"
                
                try:
                    clip1 = VideoFileClip(job['anchor'])
                    clip2 = VideoFileClip(job['event'])
                    
                    # 1. APPLY TRIMMING (SUBCLIP) FIRST
                    if job['anchor_start'] != "00:00" or job['anchor_end']:
                        clip1 = clip1.subclip(job['anchor_start'], job['anchor_end'])
                        
                    if job['event_start'] != "00:00" or job['event_end']:
                        clip2 = clip2.subclip(job['event_start'], job['event_end'])
                    
                    # 2. Handle Duration Loop
                    max_duration = max(clip1.duration, clip2.duration)
                    if clip1.duration < max_duration: clip1 = clip1.fx(vfx.loop, duration=max_duration)
                    if clip2.duration < max_duration: clip2 = clip2.fx(vfx.loop, duration=max_duration)

                    # 3. Crop and Fill Logic (No Black Bars)
                    def crop_and_fill(clip, target_w=960, target_h=1080):
                        current_ratio = clip.w / clip.h
                        target_ratio = target_w / target_h

                        if current_ratio > target_ratio:
                            clip = clip.resize(height=target_h)
                            clip = clip.crop(x_center=clip.w/2, width=target_w)
                        else:
                            clip = clip.resize(width=target_w)
                            clip = clip.crop(y_center=clip.h/2, height=target_h)
                        return clip

                    clip1 = crop_and_fill(clip1)
                    clip2 = crop_and_fill(clip2)
                    
                    # 4. Position Flush with Edges
                    clip1 = clip1.set_position((0, 0))
                    clip2 = clip2.set_position((960, 0))
                    
                    # 5. Canvas & Layers
                    canvas = ColorClip(size=(1920, 1080), color=(0,0,0), duration=max_duration)
                    video_layers = [canvas, clip1, clip2]
                    
                    if job['logo']:
                        logo_clip = ImageClip(job['logo']).resize(height=100)
                        logo_clip = logo_clip.set_position((1920 - logo_clip.w - 50, 50)).set_duration(max_duration)
                        video_layers.append(logo_clip)
                    
                    # 6. Audio Handling
                    final_audio = None
                    if job['audio'] == "Keep Anchor Audio" and clip1.audio: final_audio = clip1.audio
                    elif job['audio'] == "Keep Event Audio" and clip2.audio: final_audio = clip2.audio
                    elif job['audio'] == "Mix Both" and clip1.audio and clip2.audio:
                        from moviepy.audio.AudioClip import CompositeAudioClip
                        final_audio = CompositeAudioClip([clip1.audio, clip2.audio])
                    else:
                        final_audio = clip1.audio or clip2.audio
                        
                    final_video = CompositeVideoClip(video_layers)
                    if final_audio: final_video = final_video.set_audio(final_audio)
                    
                    os.makedirs("finished_renders", exist_ok=True)
                    out_path = f"finished_renders/{job['name']}_{job['id']}.mp4"
                    
                    # 7. RENDER
                    final_video.write_videofile(out_path, codec="libx264", audio_codec="aac", preset="ultrafast")
                    
                    job['output'] = out_path
                    job['status'] = "Done"
                    
                finally:
                    # CLEANUP TO SAVE RAM FOR THE NEXT VIDEO
                    try: clip1.close() 
                    except: pass
                    try: clip2.close() 
                    except: pass
                    if job['logo']:
                        try: logo_clip.close()
                        except: pass
                    
                    # Delete the temp inputs to save hard drive space
                    if os.path.exists(job['anchor']): os.remove(job['anchor'])
                    if os.path.exists(job['event']): os.remove(job['event'])
                    if job['logo'] and os.path.exists(job['logo']): os.remove(job['logo'])
                
                # Refresh UI after each video finishes
                st.rerun() 
        
        st.session_state.is_processing = False
        st.success("🎉 Entire queue is finished!")