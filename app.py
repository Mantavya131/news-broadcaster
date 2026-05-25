# import streamlit as st
# import PIL.Image
# import os
# import uuid

# # --- THE FIX: Monkey Patch for Pillow 10+ ---
# if not hasattr(PIL.Image, 'ANTIALIAS'):
#     PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
# # ---------------------------------------------

# from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, ImageClip, concatenate_videoclips
# import moviepy.video.fx.all as vfx

# st.set_page_config(page_title="Batch News Broadcaster", layout="wide")

# # --- INITIALIZE SESSION STATE ---
# if 'job_queue' not in st.session_state:
#     st.session_state.job_queue = []
# if 'is_processing' not in st.session_state:
#     st.session_state.is_processing = False

# st.title("📺 Batch News Broadcast Generator")
# st.markdown("Upload multiple clips per side, preview durations, and stitch them seamlessly.")

# # ==========================================
# # SECTION 1: ADD TO QUEUE
# # ==========================================
# st.subheader("1. Build Your Broadcast Sequence")

# with st.container(border=True):
#     col1, col2 = st.columns(2)
    
#     # --- LEFT SIDE (ANCHORS) ---
#     with col1:
#         st.markdown("### 🗣️ Anchor Videos (Left)")
#         anchor_files = st.file_uploader("Upload Anchor Clips", type=['mp4', 'mov', 'avi'], accept_multiple_files=True, key="anchor_up")
#         anchor_configs = []
        
#         if anchor_files:
#             for i, f in enumerate(anchor_files):
#                 with st.expander(f"Clip {i+1}: {f.name}", expanded=True):
#                     st.video(f) # IN-APP PREVIEW
#                     c1, c2 = st.columns(2)
#                     with c1: a_start = st.text_input("Start (MM:SS)", value="00:00", key=f"a_start_{i}")
#                     with c2: a_end = st.text_input("End (MM:SS)", value="", placeholder="Leave blank for full", key=f"a_end_{i}")
#                     anchor_configs.append({"file": f, "start": a_start, "end": a_end})

#     # --- RIGHT SIDE (EVENTS) ---
#     with col2:
#         st.markdown("### 🎥 Event Videos (Right)")
#         event_files = st.file_uploader("Upload Event Clips", type=['mp4', 'mov', 'avi'], accept_multiple_files=True, key="event_up")
#         event_configs = []
        
#         if event_files:
#             for i, f in enumerate(event_files):
#                 with st.expander(f"Clip {i+1}: {f.name}", expanded=True):
#                     st.video(f) # IN-APP PREVIEW
#                     c1, c2 = st.columns(2)
#                     with c1: e_start = st.text_input("Start (MM:SS)", value="00:00", key=f"e_start_{i}")
#                     with c2: e_end = st.text_input("End (MM:SS)", value="", placeholder="Leave blank for full", key=f"e_end_{i}")
#                     event_configs.append({"file": f, "start": e_start, "end": e_end})

#     st.divider()
    
#     # --- GLOBAL SETTINGS ---
#     col3, col4 = st.columns(2)
#     with col3:
#         audio_choice = st.radio("Choose audio source:", ("Keep Anchor Audio", "Keep Event Audio", "Mix Both"), key="audio_up")
#     with col4:
#         logo_file = st.file_uploader("Upload Channel Logo (PNG)", type=['png'], key="logo_up")

#     job_name = st.text_input("Name this broadcast (e.g., 'Morning_Segment_1')")

#     if st.button("➕ Add Sequence to Queue", type="primary"):
#         if anchor_files and event_files and job_name:
#             job_id = str(uuid.uuid4())[:8]
#             os.makedirs("temp_queue", exist_ok=True)
            
#             # Save all Anchor files
#             saved_anchors = []
#             for i, cfg in enumerate(anchor_configs):
#                 path = f"temp_queue/{job_id}_anchor_{i}.mp4"
#                 with open(path, "wb") as f_out: f_out.write(cfg["file"].read())
#                 saved_anchors.append({"path": path, "start": cfg["start"], "end": cfg["end"] if cfg["end"].strip() != "" else None})

#             # Save all Event files
#             saved_events = []
#             for i, cfg in enumerate(event_configs):
#                 path = f"temp_queue/{job_id}_event_{i}.mp4"
#                 with open(path, "wb") as f_out: f_out.write(cfg["file"].read())
#                 saved_events.append({"path": path, "start": cfg["start"], "end": cfg["end"] if cfg["end"].strip() != "" else None})
            
#             # Save Logo
#             p_logo = None
#             if logo_file:
#                 p_logo = f"temp_queue/{job_id}_logo.png"
#                 with open(p_logo, "wb") as f_out: f_out.write(logo_file.read())

#             # Add to memory
#             st.session_state.job_queue.append({
#                 "id": job_id,
#                 "name": job_name,
#                 "anchors": saved_anchors,
#                 "events": saved_events,
#                 "logo": p_logo,
#                 "audio": audio_choice,
#                 "status": "Waiting",
#                 "output": None
#             })
#             st.success(f"Added '{job_name}' to queue!")
#             st.rerun() 
#         else:
#             st.error("Please upload at least one video per side and name the job.")

# # ==========================================
# # SECTION 2: QUEUE DASHBOARD & PROCESSING
# # ==========================================
# st.divider()
# st.subheader(f"2. Processing Queue ({len(st.session_state.job_queue)} Items)")

# for job in st.session_state.job_queue:
#     if job['status'] == "Waiting":
#         st.info(f"⏳ **Waiting:** {job['name']}")
#     elif job['status'] == "Processing":
#         st.warning(f"⚙️ **Processing right now:** {job['name']}")
#     elif job['status'] == "Done":
#         col_a, col_b = st.columns([3, 1])
#         with col_a: st.success(f"✅ **Finished:** {job['name']}")
#         with col_b:
#             with open(job['output'], "rb") as f:
#                 st.download_button(label="⬇️ Download", data=f, file_name=f"{job['name']}.mp4", mime="video/mp4", key=f"dl_{job['id']}")

# if len(st.session_state.job_queue) > 0:
#     waiting_jobs = [j for j in st.session_state.job_queue if j['status'] == "Waiting"]
    
#     if len(waiting_jobs) > 0 and not st.session_state.is_processing:
#         if st.button("🚀 Start Processing Queue"):
#             st.session_state.is_processing = True
#             st.rerun()

#     if st.session_state.is_processing:
#         for job in st.session_state.job_queue:
#             if job['status'] == "Waiting":
#                 job['status'] = "Processing"
                
#                 try:
#                     # --- HELPER: Process and Stitch Multiple Clips ---
#                     def build_master_clip(clip_data_list):
#                         processed_clips = []
#                         for c_data in clip_data_list:
#                             c = VideoFileClip(c_data['path'])
#                             if c_data['start'] != "00:00" or c_data['end']:
#                                 c = c.subclip(c_data['start'], c_data['end'])
#                             processed_clips.append(c)
#                         if len(processed_clips) == 1:
#                             return processed_clips[0]
#                         return concatenate_videoclips(processed_clips, method="compose")

#                     # 1. Stitch Left and Right Master Clips
#                     clip1 = build_master_clip(job['anchors'])
#                     clip2 = build_master_clip(job['events'])
                    
#                     # 2. Handle Duration Loop (Match the longest side)
#                     max_duration = max(clip1.duration, clip2.duration)
#                     if clip1.duration < max_duration: clip1 = clip1.fx(vfx.loop, duration=max_duration)
#                     if clip2.duration < max_duration: clip2 = clip2.fx(vfx.loop, duration=max_duration)

#                     # 3. Crop and Fill Logic (No Black Bars)
#                     def crop_and_fill(clip, target_w=960, target_h=1080):
#                         current_ratio = clip.w / clip.h
#                         target_ratio = target_w / target_h

#                         if current_ratio > target_ratio:
#                             clip = clip.resize(height=target_h)
#                             clip = clip.crop(x_center=clip.w/2, width=target_w)
#                         else:
#                             clip = clip.resize(width=target_w)
#                             clip = clip.crop(y_center=clip.h/2, height=target_h)
#                         return clip

#                     clip1 = crop_and_fill(clip1)
#                     clip2 = crop_and_fill(clip2)
                    
#                     # 4. Position Flush with Edges
#                     clip1 = clip1.set_position((0, 0))
#                     clip2 = clip2.set_position((960, 0))
                    
#                     # 5. Canvas & Layers
#                     canvas = ColorClip(size=(1920, 1080), color=(0,0,0), duration=max_duration)
#                     video_layers = [canvas, clip1, clip2]
                    
#                     if job['logo']:
#                         logo_clip = ImageClip(job['logo']).resize(height=100)
#                         logo_clip = logo_clip.set_position((1920 - logo_clip.w - 50, 50)).set_duration(max_duration)
#                         video_layers.append(logo_clip)
                    
#                     # 6. Audio Handling
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
                    
#                     # 7. RENDER
#                     final_video.write_videofile(out_path, codec="libx264", audio_codec="aac", preset="ultrafast")
                    
#                     job['output'] = out_path
#                     job['status'] = "Done"
                    
#                 finally:
#                     # CLEANUP MEMORY AND FILES
#                     try: clip1.close() 
#                     except: pass
#                     try: clip2.close() 
#                     except: pass
#                     if job['logo']:
#                         try: logo_clip.close()
#                         except: pass
                    
#                     # Delete temp hard drive files
#                     for a in job['anchors']:
#                         if os.path.exists(a['path']): os.remove(a['path'])
#                     for e in job['events']:
#                         if os.path.exists(e['path']): os.remove(e['path'])
#                     if job['logo'] and os.path.exists(job['logo']): os.remove(job['logo'])
                
#                 st.rerun() 
        
#         st.session_state.is_processing = False
#         st.success("🎉 Entire queue is finished!")






import streamlit as st
import PIL.Image
import os
import uuid

# --- THE FIX: Monkey Patch for Pillow 10+ ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
# ---------------------------------------------

from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, ImageClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
from moviepy.audio.AudioClip import CompositeAudioClip

st.set_page_config(page_title="Batch News Broadcaster", layout="wide")

# --- INITIALIZE SESSION STATE ---
if 'job_queue' not in st.session_state:
    st.session_state.job_queue = []
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

st.title("📺 Batch News Broadcast Generator")
st.markdown("Upload multiple clips per side, preview durations, and stitch them seamlessly.")

# ==========================================
# SECTION 1: ADD TO QUEUE
# ==========================================
st.subheader("1. Build Your Broadcast Sequence")

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    # --- LEFT SIDE (ANCHORS) ---
    with col1:
        st.markdown("### 🗣️ Anchor Videos (Left)")
        anchor_files = st.file_uploader("Upload Anchor Clips", type=['mp4', 'mov', 'avi'], accept_multiple_files=True, key="anchor_up")
        anchor_configs = []
        
        if anchor_files:
            for i, f in enumerate(anchor_files):
                with st.expander(f"Clip {i+1}: {f.name}", expanded=True):
                    st.video(f) # IN-APP PREVIEW
                    c1, c2 = st.columns(2)
                    with c1: a_start = st.text_input("Start (MM:SS)", value="00:00", key=f"a_start_{i}")
                    with c2: a_end = st.text_input("End (MM:SS)", value="", placeholder="Leave blank for full", key=f"a_end_{i}")
                    anchor_configs.append({"file": f, "start": a_start, "end": a_end})

    # --- RIGHT SIDE (EVENTS) ---
    with col2:
        st.markdown("### 🎥 Event Videos (Right)")
        event_files = st.file_uploader("Upload Event Clips", type=['mp4', 'mov', 'avi'], accept_multiple_files=True, key="event_up")
        event_configs = []
        
        if event_files:
            for i, f in enumerate(event_files):
                with st.expander(f"Clip {i+1}: {f.name}", expanded=True):
                    st.video(f) # IN-APP PREVIEW
                    c1, c2 = st.columns(2)
                    with c1: e_start = st.text_input("Start (MM:SS)", value="00:00", key=f"e_start_{i}")
                    with c2: e_end = st.text_input("End (MM:SS)", value="", placeholder="Leave blank for full", key=f"e_end_{i}")
                    event_configs.append({"file": f, "start": e_start, "end": e_end})

    st.divider()
    
    # --- GLOBAL SETTINGS ---
    col3, col4 = st.columns(2)
    with col3:
        audio_choice = st.radio("Choose audio source:", ("Keep Anchor Audio", "Keep Event Audio", "Mix Both"), key="audio_up")
    with col4:
        logo_file = st.file_uploader("Upload Channel Logo (PNG)", type=['png'], key="logo_up")

    job_name = st.text_input("Name this broadcast (e.g., 'Morning_Segment_1')")

    if st.button("➕ Add Sequence to Queue", type="primary"):
        if anchor_files and event_files and job_name:
            job_id = str(uuid.uuid4())[:8]
            os.makedirs("temp_queue", exist_ok=True)
            
            # Save all Anchor files
            saved_anchors = []
            for i, cfg in enumerate(anchor_configs):
                path = f"temp_queue/{job_id}_anchor_{i}.mp4"
                with open(path, "wb") as f_out: f_out.write(cfg["file"].read())
                saved_anchors.append({"path": path, "start": cfg["start"], "end": cfg["end"] if cfg["end"].strip() != "" else None})

            # Save all Event files
            saved_events = []
            for i, cfg in enumerate(event_configs):
                path = f"temp_queue/{job_id}_event_{i}.mp4"
                with open(path, "wb") as f_out: f_out.write(cfg["file"].read())
                saved_events.append({"path": path, "start": cfg["start"], "end": cfg["end"] if cfg["end"].strip() != "" else None})
            
            # Save Logo
            p_logo = None
            if logo_file:
                p_logo = f"temp_queue/{job_id}_logo.png"
                with open(p_logo, "wb") as f_out: f_out.write(logo_file.read())

            # Add to memory
            st.session_state.job_queue.append({
                "id": job_id,
                "name": job_name,
                "anchors": saved_anchors,
                "events": saved_events,
                "logo": p_logo,
                "audio": audio_choice,
                "status": "Waiting",
                "output": None
            })
            st.success(f"Added '{job_name}' to queue!")
            st.rerun() 
        else:
            st.error("Please upload at least one video per side and name the job.")

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
        with col_a: st.success(f"✅ **Finished:** {job['name']}")
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
                    # --- HELPER: Process and Stitch Multiple Clips ---
                    def build_master_clip(clip_data_list):
                        processed_clips = []
                        for c_data in clip_data_list:
                            c = VideoFileClip(c_data['path'])
                            if c_data['start'] != "00:00" or c_data['end']:
                                c = c.subclip(c_data['start'], c_data['end'])
                            processed_clips.append(c)
                        if len(processed_clips) == 1:
                            return processed_clips[0]
                        return concatenate_videoclips(processed_clips, method="compose")

                    # 1. Stitch Left and Right Master Clips
                    clip1 = build_master_clip(job['anchors'])
                    clip2 = build_master_clip(job['events'])
                    
                    # --- THE FIX: Separate Audio Before Looping ---
                    audio1 = clip1.audio
                    audio2 = clip2.audio
                    clip1 = clip1.without_audio()
                    clip2 = clip2.without_audio()
                    
                    # 2. Handle Duration Loop (Match the longest side)
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
                    
                    # 6. Audio Handling (Safely padded with silence)
                    base_audio = None
                    if job['audio'] == "Keep Anchor Audio" and audio1: base_audio = audio1
                    elif job['audio'] == "Keep Event Audio" and audio2: base_audio = audio2
                    elif job['audio'] == "Mix Both" and audio1 and audio2:
                        base_audio = CompositeAudioClip([audio1, audio2])
                    else:
                        base_audio = audio1 or audio2
                        
                    final_video = CompositeVideoClip(video_layers)
                    
                    if base_audio:
                        final_audio = CompositeAudioClip([base_audio]).set_duration(max_duration)
                        final_video = final_video.set_audio(final_audio)
                    
                    os.makedirs("finished_renders", exist_ok=True)
                    out_path = f"finished_renders/{job['name']}_{job['id']}.mp4"
                    
                    # 7. RENDER
                    final_video.write_videofile(out_path, codec="libx264", audio_codec="aac", preset="ultrafast")
                    
                    job['output'] = out_path
                    job['status'] = "Done"
                    
                finally:
                    # CLEANUP MEMORY AND FILES
                    try: clip1.close() 
                    except: pass
                    try: clip2.close() 
                    except: pass
                    if job['logo']:
                        try: logo_clip.close()
                        except: pass
                    
                    # Delete temp hard drive files
                    for a in job['anchors']:
                        if os.path.exists(a['path']): os.remove(a['path'])
                    for e in job['events']:
                        if os.path.exists(e['path']): os.remove(e['path'])
                    if job['logo'] and os.path.exists(job['logo']): os.remove(job['logo'])
                
                st.rerun() 
        
        st.session_state.is_processing = False
        st.success("🎉 Entire queue is finished!")