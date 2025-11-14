import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import json
from io import BytesIO

def hex_to_rgb(hex_color):
    """Convert hex colour to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex colour"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def interpolate_color(color1, color2, steps, current_step):
    """Interpolate between two colours at fixed gradient steps"""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    r = r1 + (r2 - r1) * current_step / steps
    g = g1 + (g2 - g1) * current_step / steps
    b = b1 + (b2 - b1) * current_step / steps
    
    return (r, g, b)

def calculate_reaction_time(trial_start_time, button_press_time):
    """Calculate reaction time from when trial started"""
    if trial_start_time and button_press_time:
        return round((button_press_time - trial_start_time) * 1000, 2)
    return None

def initialize_session_state():
    """Initialize all session state variables"""
    if 'phase' not in st.session_state:
        st.session_state.phase = 'setup'  # setup, practice, main, results
    if 'current_trial' not in st.session_state:
        st.session_state.current_trial = 0
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'trial_start_time' not in st.session_state:
        st.session_state.trial_start_time = time.time()
    if 'last_update_time' not in st.session_state:
        st.session_state.last_update_time = time.time()
    if 'last_step_change_time' not in st.session_state:
        st.session_state.last_step_change_time = time.time()
    if 'next_interval' not in st.session_state:
        st.session_state.next_interval = random.uniform(0.5, 2.0)
    if 'all_results' not in st.session_state:
        st.session_state.all_results = []
    if 'current_trial_results' not in st.session_state:
        st.session_state.current_trial_results = []
    if 'participant_name' not in st.session_state:
        st.session_state.participant_name = ""
    if 'gender' not in st.session_state:
        st.session_state.gender = "Male"
    if 'age' not in st.session_state:
        st.session_state.age = 18
    if 'sleep_hours' not in st.session_state:
        st.session_state.sleep_hours = 8.0
    if 'spectra_order' not in st.session_state:
        st.session_state.spectra_order = []
    if 'false_alarms' not in st.session_state:
        st.session_state.false_alarms = 0
    if 'show_instructions' not in st.session_state:
        st.session_state.show_instructions = True
    if 'button_disabled' not in st.session_state:
        st.session_state.button_disabled = False
    if 'read_instructions' not in st.session_state:
        st.session_state.read_instructions = False
    if 'trial_complete' not in st.session_state:
        st.session_state.trial_complete = False
    if 'results_saved' not in st.session_state:
        st.session_state.results_saved = False

def get_spectra_list():
    """Get predefined colour spectra"""
    return {
        "Red to Orange": ("#FF0000", "#FF8800"),
        "Yellow to Green": ("#FFFF00", "#00FF00"),
        "Blue to Purple": ("#0000FF", "#8000FF"),
    }

def main():
    st.set_page_config(page_title="Enhanced Colour Perception Test", layout="wide", initial_sidebar_state="expanded")
    
    initialize_session_state()
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .big-font {
            font-size: 24px !important;
            font-weight: bold;
        }
        .success-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #d4edda;
            border: 2px solid #28a745;
            margin: 10px 0;
        }
        .warning-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            margin: 10px 0;
        }
        .instruction-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #e8f4fd;
            border: 2px solid #0d6efd;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🎨 Enhanced Colour Perception Test")
    st.markdown("*Advanced Research Edition with Practice Trials & Reaction Time Measurement*")
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Experiment Configuration")
        
        # Phase indicator
        phase_emoji = {
            'setup': '📋',
            'practice': '🎯',
            'main': '🔬',
            'results': '📊'
        }
        st.info(f"{phase_emoji.get(st.session_state.phase, '📋')} **Current Phase:** {st.session_state.phase.upper()}")
        st.markdown("---")
        
        if st.session_state.phase == 'setup':
            # Participant information
            st.subheader("👤 Participant Information")
            participant_name = st.text_input("Participant Name *", value=st.session_state.participant_name, 
                                          help="Your name for this experiment")
            gender = st.selectbox("Gender *", ["Male", "Female", "Other", "Prefer not to say"], 
                                 index=["Male", "Female", "Other", "Prefer not to say"].index(st.session_state.gender) if st.session_state.gender in ["Male", "Female", "Other", "Prefer not to say"] else 0)
            age = st.number_input("Age *", min_value=18, max_value=100, value=st.session_state.age)
            sleep_hours = st.number_input("🛌 Hours of Sleep (Last Night) *", min_value=0.0, max_value=24.0, value=st.session_state.sleep_hours, step=0.5,
                                        help="Number of hours you slept last night")
            
        else:
            # Show current trial info during experiment
            if st.session_state.phase in ['practice', 'main']:
                st.subheader("📍 Current Trial")
                if st.session_state.phase == 'main':
                    total_trials = len(st.session_state.spectra_order)
                    st.metric("Trial Progress", f"{st.session_state.current_trial + 1}/{total_trials}")
                    current_spectrum = st.session_state.spectra_order[st.session_state.current_trial]
                    st.info(f"**Spectrum:** {current_spectrum['spectrum_name']}")
                else:
                    st.info("**PRACTICE TRIAL**")

                st.metric("False Alarms", st.session_state.false_alarms)
    
    # Main content area
    if st.session_state.phase == 'setup':
        render_setup_phase(participant_name, gender, age, sleep_hours)
    
    elif st.session_state.phase == 'practice':
        render_practice_phase()
    
    elif st.session_state.phase == 'main':
        render_main_experiment()
    
    elif st.session_state.phase == 'results':
        render_results_phase()

def render_setup_phase(participant_name, gender, age, sleep_hours):
    """Render the setup phase"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Instructions & Declaration")
        
        st.markdown("""
        <div class="instruction-box" style="color:#856404; background-color:#fff3cd; border-color:#ffeeba;">
        <h3>📖 Experiment Instructions</h3>
        
        **Please read carefully before proceeding:**
        
        ### What You'll Do:
        - You will watch a colored box that gradually changes color
        - Press the **"The color has changed!"** button **ONCE** as soon as you notice any color change
        - The button will disappear after you click it
        - Once you press the button, you can immediately proceed to the next trial
        - There will be a practice trial followed by 3 main trials
        
        ### Important Guidelines:
        - Focus on the color box throughout each trial
        - Click **ONLY WHEN** you visually detect a change
        - Do not anticipate changes - wait until you actually see them
        - Each click should be a genuine detection, not a guess
        - Avoid distractions during the experiment
        
        ### Experiment Structure:
        - **Practice Trial**: 1 trial to familiarize yourself
        - **Main Experiment**: 3 color spectrums, 1 trial each (3 total trials)
        - Color transitions: Red→Orange, Yellow→Green, Blue→Purple
        
        ### Technical Notes:
        - Ensure consistent lighting and screen brightness
        - Sit at a comfortable distance from your screen
        - The experiment will take approximately 5-10 minutes
        </div>
        """, unsafe_allow_html=True)
        
        # Declaration checkbox
        st.markdown("---")
        read_instructions = st.checkbox(
            "✅ I have read and understood the instructions above, and I agree to participate in this experiment",
            value=st.session_state.read_instructions
        )
        st.session_state.read_instructions = read_instructions
        
        # Validation
        errors = []
        if not participant_name:
            errors.append("⚠️ Participant Name is required")
        if not read_instructions:
            errors.append("⚠️ Please read and agree to the instructions")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("✅ All required information provided")
            
            # Show experiment summary
            st.info(f"""
            **Experiment Summary:**
            - Participant: {participant_name} ({gender}, {age} years)
            - Sleep Hours: {sleep_hours}
            - Spectra: 3 fixed color transitions
            - Trials per spectrum: 1
            - Total trials: 3
            - Practice trial: Yes
            - Estimated duration: 5-10 minutes
            """)
            
            if st.button("🎯 Start Experiment", type="primary", use_container_width=True):
                # Save configuration
                st.session_state.participant_name = participant_name
                st.session_state.gender = gender
                st.session_state.age = age
                st.session_state.sleep_hours = sleep_hours
                st.session_state.trials_per_spectrum = 1
                st.session_state.total_steps = 50
                st.session_state.min_interval = 0.5
                st.session_state.max_interval = 2.0
                st.session_state.experiment_start_time = datetime.now()
                
                # Create fixed trial order with 3 spectrums, 1 trial each
                spectra = get_spectra_list()
                trial_list = []
                for spectrum_name in spectra.keys():  # All 3 fixed spectrums
                    trial_list.append({
                        'spectrum_name': spectrum_name,
                        'start_color': spectra[spectrum_name][0],
                        'end_color': spectra[spectrum_name][1],
                        'trial_number': 1
                    })
                
                # Randomize order but keep all trials
                random.shuffle(trial_list)
                st.session_state.spectra_order = trial_list
                
                # Start with practice phase
                st.session_state.phase = 'practice'
                st.session_state.current_step = 0
                st.session_state.current_trial_results = []
                st.session_state.practice_start_color = "#FF0000"
                st.session_state.practice_end_color = "#FFFF00"
                st.session_state.button_disabled = False
                st.session_state.trial_complete = False
                
                st.rerun()
    
    with col2:
        st.subheader("ℹ️ About This Test")
        st.markdown("""
        This enhanced colour perception test measures:
        
        - **Detection accuracy**: Where you notice changes
        - **Reaction time**: How quickly you respond
        - **Sensitivity**: Subtle vs obvious changes
        - **Consistency**: Performance across trials
        
        **Research Purpose:**
        Your data helps research on colour perception differences and visual sensitivity.
        
        **Privacy:**
        - Your data is anonymized
        - Used only for research purposes
        - You can withdraw at any time
        """)

        st.markdown("---")
            
        # Fixed experiment design - everyone gets the same 3 spectrums
        st.subheader("🔬 Experiment Design")
        st.markdown("""
        **Fixed Spectra (Same for all participants):**
        - Red to Orange
        - Yellow to Green  
        - Blue to Purple
        """)
        
        trials_per_spectrum = 1
        include_practice = True
        
        st.markdown("---")
        
        # Test parameters
        st.subheader("⏱️ Timing Parameters")
        total_steps = 50
        min_interval = 0.5
        max_interval = 2.0
        
        st.markdown(f"""
        **Fixed Parameters:**
        - Gradient Steps: {total_steps}
        - Interval Range: {min_interval}-{max_interval} seconds
        - Trials per Spectrum: {trials_per_spectrum}
        - Total Trials: 3
        """)
            

def render_practice_phase():
    """Render the practice trial phase"""
    
    # Initialize trial start time if not set or if trial was just reset
    if 'trial_start_time' not in st.session_state or st.session_state.current_step == 0:
        st.session_state.trial_start_time = time.time()

    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("🎯 **PRACTICE TRIAL** - This trial is not recorded. Get familiar with the test!")
        
        # Run the colour display
        trial_complete = run_colour_trial(
            start_color=st.session_state.practice_start_color,
            end_color=st.session_state.practice_end_color,
            is_practice=True
        )
        
        if trial_complete or st.session_state.trial_complete:
            st.success("✅ Practice trial complete!")
            st.markdown("You detected the colour change during practice.")
            
            if st.button("▶️ Start Main Experiment", type="primary", use_container_width=True):
                st.session_state.phase = 'main'
                st.session_state.current_trial = 0
                st.session_state.current_step = 0
                st.session_state.current_trial_results = []
                st.session_state.false_alarms = 0
                st.session_state.button_disabled = False
                st.session_state.trial_complete = False
                st.session_state.results_saved = False  # Reset for main experiment
                st.rerun()
    
    with col2:
        st.subheader("💡 Practice Tips")
        st.markdown("""
        - Watch the colour box carefully
        - Press button **ONCE** when you see a change
        - The button will disappear after clicking
        - You can proceed immediately after detection
        - Don't anticipate - wait for actual changes
        - This is just practice - take your time
        """)

def render_main_experiment():
    """Render the main experiment phase"""
    
    # Initialize trial start time if not set or if trial was just reset
    if 'trial_start_time' not in st.session_state or st.session_state.current_step == 0:
        st.session_state.trial_start_time = time.time()

    current_trial_info = st.session_state.spectra_order[st.session_state.current_trial]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Trial header
        total_trials = len(st.session_state.spectra_order)
        st.markdown(f"### Trial {st.session_state.current_trial + 1} of {total_trials}")
        st.caption(f"Spectrum: **{current_trial_info['spectrum_name']}**")
        
        # Run the colour display
        trial_complete = run_colour_trial(
            start_color=current_trial_info['start_color'],
            end_color=current_trial_info['end_color'],
            is_practice=False
        )
        
        # If trial is complete (either by detection or timeout), show next options
        if trial_complete or st.session_state.trial_complete:
            # Save trial results if we have any (only once per trial)
            if st.session_state.current_trial_results and not st.session_state.results_saved:
                result = st.session_state.current_trial_results[0]
                result['spectrum'] = current_trial_info['spectrum_name']
                result['overall_trial'] = st.session_state.current_trial + 1
                st.session_state.all_results.append(result)
                st.session_state.results_saved = True  # Mark as saved
                is_false_alarm = result.get('false_alarm', False)
            elif st.session_state.results_saved and st.session_state.all_results:
                # Already saved, just get the false alarm status
                is_false_alarm = st.session_state.all_results[-1].get('false_alarm', False)
            else:
                is_false_alarm = False
            
            # Check if more trials
            if is_false_alarm or st.session_state.current_trial + 1 < total_trials:
                if is_false_alarm:
                    st.error(f"⚠️ Trial {st.session_state.current_trial + 1} marked as False Alarm - retry required!")
                    button_text = "🔄 Retry Trial"
                else:
                    st.success(f"✅ Trial {st.session_state.current_trial + 1} complete!")
                    button_text = "➡️ Next Trial"

                st.info("Ready for the next trial when you are.")
                
                col_a, col_b = st.columns(2)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(button_text, type="primary", use_container_width=True):
                        if not is_false_alarm:
                            st.session_state.current_trial += 1
                        # Reset for next/retry trial
                        st.session_state.current_step = 0
                        st.session_state.current_trial_results = []
                        st.session_state.button_disabled = False
                        st.session_state.trial_complete = False
                        st.session_state.results_saved = False  # Reset for next trial
                        st.session_state.trial_start_time = time.time()
                        st.rerun()
                
                with col_b:
                    if st.button("⏸️ Take a Break", use_container_width=True):
                        st.info("Take your time. Click next when ready to continue.")
            
            else:
                # All trials complete
                st.balloons()
                st.success("🎉 All trials complete! Excellent work!")
                
                if st.button("📊 View Results", type="primary", use_container_width=True):
                    st.session_state.phase = 'results'
                    st.session_state.experiment_end_time = datetime.now()
                    st.rerun()
    
    with col2:
        st.subheader("💡 Practice Tips")
        st.markdown("""
        - Watch the colour box carefully
        - Press button **ONCE** when you see a change
        - The button will disappear after clicking
        - You can proceed immediately after detection
        - Don't anticipate - wait for actual changes
        - This is just practice - take your time
        """)

def run_colour_trial(start_color, end_color, is_practice):
    """Run a single colour trial and return whether it's complete"""

    if st.session_state.current_step >= st.session_state.total_steps or st.session_state.trial_complete:
        return True

    current_rgb = interpolate_color(
        start_color,
        end_color,
        st.session_state.total_steps,
        st.session_state.current_step
    )
    current_hex = rgb_to_hex(current_rgb)

    st.markdown(f"""
        <div style="
            background-color: {current_hex};
            height: 450px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            margin: 20px 0;
        ">
        </div>
    """, unsafe_allow_html=True)
    
    # Detection button - only show if not disabled and trial not complete
    if not st.session_state.button_disabled and not st.session_state.trial_complete:
        button_pressed = st.button(
            "👁️ The color has changed!",
            type="primary",
            use_container_width=True,
            key=f"detect_{st.session_state.current_step}_{st.session_state.current_trial}"
        )
        
        if button_pressed:
            button_press_time = time.time()
            reaction_time = calculate_reaction_time(st.session_state.trial_start_time, button_press_time)
            is_false_alarm = reaction_time < 2000 if reaction_time else False
            
            result = {
                "participant_name": st.session_state.participant_name,
                "gender": st.session_state.gender,
                "age": st.session_state.age,
                "sleep_hours": st.session_state.sleep_hours,
                "percentage_complete": round((st.session_state.current_step / st.session_state.total_steps * 100), 2),
                "hex_code": current_hex,
                "rgb": f"({int(current_rgb[0])}, {int(current_rgb[1])}, {int(current_rgb[2])})",
                "reaction_time_ms": reaction_time,
                "false_alarm": is_false_alarm,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            }
            
            st.session_state.current_trial_results = [result]
            
            # Mark trial as complete and disable button
            st.session_state.button_disabled = True
            st.session_state.trial_complete = True
            
            # Visual feedback
            if is_false_alarm:
                st.error(f"⚠️ False Alarm! Response too fast ({reaction_time} ms). You must retry this trial.")
                st.session_state.false_alarms += 1
            else:
                st.success(f"✓ Change detected! (RT: {reaction_time} ms)")
            
            st.info("🎯 **Trial complete!** You can proceed to the next trial.")
            st.rerun()
    
    # If trial is complete due to detection, show completion message
    elif st.session_state.trial_complete:
        st.success("✅ **Change detected!** Trial complete - ready for next trial.")
    
    # Auto-advance colour (only if trial not complete)
    if not st.session_state.trial_complete:
        current_time = time.time()
        if current_time - st.session_state.last_update_time >= st.session_state.next_interval:
            st.session_state.current_step += 1
            st.session_state.last_update_time = current_time
            st.session_state.last_step_change_time = current_time
            st.session_state.next_interval = random.uniform(
                st.session_state.min_interval,
                st.session_state.max_interval
            )
            st.rerun()
        else:
            time.sleep(0.1)
            st.rerun()
    
    return False

def render_results_phase():
    """Render the results and analysis phase"""
    
    st.success("✅ Experiment Complete!")
    
    # Calculate duration
    if hasattr(st.session_state, 'experiment_start_time') and hasattr(st.session_state, 'experiment_end_time'):
        duration = st.session_state.experiment_end_time - st.session_state.experiment_start_time
        duration_minutes = duration.total_seconds() / 60
    else:
        duration_minutes = 0
    
    # Summary metrics
    st.subheader("📈 Performance Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Trials", len(st.session_state.spectra_order))
    with col2:
        st.metric("Duration", f"{duration_minutes:.1f} min")
    
    st.markdown("---")
    
    # Detailed results
    if st.session_state.all_results:
        st.subheader("📊 Detailed Results")
        
        df = pd.DataFrame(st.session_state.all_results)
        
        # Display participant info once
        st.info(f"**Participant:** {st.session_state.participant_name} | **Gender:** {st.session_state.gender} | **Age:** {st.session_state.age} | **Sleep Hours:** {st.session_state.sleep_hours}")

        display_df = df[['overall_trial', 'spectrum', 'percentage_complete', 'hex_code', 'rgb', 'reaction_time_ms', 'false_alarm']].copy()
        display_df.columns = ['Trial #', 'Spectrum', '% Complete', 'Hex', 'RGB', 'RT (ms)', 'False Alarm']

        display_df['% Complete'] = display_df['% Complete'].apply(lambda x: f"{x:.1f}%")
        display_df['RT (ms)'] = display_df['RT (ms)'].apply(lambda x: f"{int(x)}" if pd.notna(x) else "—")
        display_df['False Alarm'] = display_df['False Alarm'].apply(lambda x: 'Yes' if x else 'No')
        
        st.dataframe(display_df, use_container_width=True)
        
        # Statistical summary
        st.subheader("📉 Statistical Analysis")
        
        valid_df = df[df['false_alarm'] == False].copy()
        if len(valid_df) > 0:
            col1, col2 = st.columns(2)
        
            with col1:
                st.markdown("**Detection Points** *(excluding false alarms)*")
                st.write(f"- Valid Trials: {len(valid_df)}")
                st.write(f"- Mean: {valid_df['percentage_complete'].mean():.1f}%")
                st.write(f"- Median: {valid_df['percentage_complete'].median():.1f}%")
                st.write(f"- Std Dev: {valid_df['percentage_complete'].std():.1f}%")
                st.write(f"- Range: {valid_df['percentage_complete'].min():.1f}% - {valid_df['percentage_complete'].max():.1f}%")
            
            with col2:
                st.markdown("**Reaction Times** *(excluding false alarms)*")
                rt_data = valid_df[valid_df['reaction_time_ms'].notna()]['reaction_time_ms']
                if len(rt_data) > 0:
                    st.write(f"- Mean: {rt_data.mean():.0f} ms")
                    st.write(f"- Median: {rt_data.median():.0f} ms")
                    st.write(f"- Std Dev: {rt_data.std():.0f} ms")
                    st.write(f"- Range: {rt_data.min():.0f} - {rt_data.max():.0f} ms")
        else:
            st.warning("No valid trials for analysis (all trials were false alarms).")
        
        # Download options
        st.markdown("---")
        st.subheader("💾 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel export
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            
            st.download_button(
                label="📥 Download Full Data (Excel)",
                data=excel_buffer,
                file_name=f"colour_perception_{st.session_state.participant_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # Summary export
            summary_data = {
                'participant_info': {
                    'name': st.session_state.participant_name,
                    'gender': st.session_state.gender,
                    'age': st.session_state.age,
                    'sleep_hours': st.session_state.sleep_hours,
                    'experiment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'performance_summary': {
                    'total_detections': len(st.session_state.all_results),
                    'mean_percentage': round(df['percentage_complete'].mean(), 2),
                    'mean_rt_ms': round(rt_data.mean(), 2) if len(rt_data) > 0 else None,
                    'duration_minutes': round(duration_minutes, 2)
                }
            }
            summary_json = json.dumps(summary_data, indent=2)
            st.download_button(
                label="📄 Download Summary (JSON)",
                data=summary_json,
                file_name=f"summary_{st.session_state.participant_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Experiment", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()