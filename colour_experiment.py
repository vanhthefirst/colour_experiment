"""
Enhanced Colour Perception Test Application
Advanced version with practice trials, multiple trials, reaction time measurement,
and comprehensive data analysis features.
"""

import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import colorsys
import json

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

def calculate_reaction_time(step_change_time, button_press_time):
    """Calculate reaction time from when color actually changed"""
    if step_change_time and button_press_time:
        return round((button_press_time - step_change_time) * 1000, 2)  # milliseconds
    return None

def initialize_session_state():
    """Initialize all session state variables"""
    if 'phase' not in st.session_state:
        st.session_state.phase = 'setup'  # setup, practice, main, results
    if 'current_trial' not in st.session_state:
        st.session_state.current_trial = 0
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
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
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = ""
    if 'gender' not in st.session_state:
        st.session_state.gender = "Male"
    if 'age' not in st.session_state:
        st.session_state.age = 18
    if 'spectra_order' not in st.session_state:
        st.session_state.spectra_order = []
    if 'false_alarms' not in st.session_state:
        st.session_state.false_alarms = 0
    if 'show_instructions' not in st.session_state:
        st.session_state.show_instructions = True

def get_spectra_list():
    """Get predefined colour spectra"""
    return {
        "Red to Orange": ("#FF0000", "#FF8800"),
        "Red to Green": ("#FF0000", "#00FF00"),
        "Yellow to Green": ("#FFFF00", "#00FF00"),
        "Blue to Purple": ("#0000FF", "#8000FF"),
        "Orange to Yellow": ("#FF8800", "#FFFF00"),
        "Green to Cyan": ("#00FF00", "#00FFFF"),
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
            participant_id = st.text_input("Participant ID *", value=st.session_state.participant_id, 
                                          help="Unique identifier for this participant")
            gender = st.selectbox("Gender *", ["Male", "Female", "Other", "Prefer not to say"], 
                                 index=["Male", "Female", "Other", "Prefer not to say"].index(st.session_state.gender) if st.session_state.gender in ["Male", "Female", "Other", "Prefer not to say"] else 0)
            age = st.number_input("Age *", min_value=18, max_value=100, value=st.session_state.age)
            
            st.markdown("---")
            
            # Experiment design
            st.subheader("🔬 Experiment Design")
            
            spectra = get_spectra_list()
            selected_spectra = st.multiselect(
                "Select Colour Spectra to Test",
                options=list(spectra.keys()),
                default=["Red to Orange", "Red to Green"],
                help="Choose which colour transitions to test"
            )
            
            trials_per_spectrum = st.number_input(
                "Trials per Spectrum",
                min_value=1,
                max_value=10,
                value=3,
                help="Number of times to repeat each spectrum for reliability"
            )
            
            randomize_order = st.checkbox(
                "Randomize Spectrum Order",
                value=True,
                help="Present spectra in random order to control for order effects"
            )
            
            include_practice = st.checkbox(
                "Include Practice Trial",
                value=True,
                help="Start with a practice trial to familiarize participants"
            )
            
            st.markdown("---")
            
            # Test parameters
            st.subheader("⏱️ Timing Parameters")
            total_steps = st.slider("Gradient Steps", 20, 100, 50, 5,
                                   help="Number of colour steps in the gradient")
            min_interval = st.slider("Minimum Interval (seconds)", 0.1, 2.0, 0.5, 0.1,
                                    help="Shortest time between colour changes")
            max_interval = st.slider("Maximum Interval (seconds)", 0.5, 5.0, 2.0, 0.1,
                                    help="Longest time between colour changes")
            
            st.markdown("---")
            
            # Display settings
            st.subheader("🖥️ Display Settings")
            show_progress = st.checkbox("Show Progress Bar", value=True)
            show_step_number = st.checkbox("Show Step Number", value=False,
                                          help="May bias participants")
            
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
                
                st.metric("Responses This Trial", len(st.session_state.current_trial_results))
                st.metric("False Alarms", st.session_state.false_alarms)
        
        st.markdown("---")
        
        # Instructions
        with st.expander("📋 Instructions", expanded=st.session_state.show_instructions):
            st.markdown("""
            ### How to Complete This Test
            
            **Setup Phase:**
            1. Enter your participant information
            2. Configure the experiment parameters
            3. Click "Start Experiment" when ready
            
            **Practice Phase:**
            - Familiarize yourself with the test
            - Press the button when you see colour changes
            - Practice trial data is not saved
            
            **Main Experiment:**
            - Focus on the colour box
            - Press "I Detect a Change!" **immediately** when you notice any colour change
            - Complete all trials without rushing
            - Take breaks between trials if needed
            
            **Important:**
            - Avoid clicking before you see a change (false alarms)
            - You can detect multiple changes per trial
            - Each trial takes 30-60 seconds
            """)
            
            if st.button("Hide Instructions"):
                st.session_state.show_instructions = False
                st.rerun()
    
    # Main content area
    if st.session_state.phase == 'setup':
        render_setup_phase(participant_id, gender, age, selected_spectra, trials_per_spectrum,
                          randomize_order, include_practice, total_steps, min_interval, max_interval,
                          show_progress, show_step_number)
    
    elif st.session_state.phase == 'practice':
        render_practice_phase()
    
    elif st.session_state.phase == 'main':
        render_main_experiment()
    
    elif st.session_state.phase == 'results':
        render_results_phase()

def render_setup_phase(participant_id, gender, age, selected_spectra, trials_per_spectrum,
                      randomize_order, include_practice, total_steps, min_interval, max_interval,
                      show_progress, show_step_number):
    """Render the setup phase"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚀 Ready to Begin")
        
        # Validation
        errors = []
        if not participant_id:
            errors.append("⚠️ Participant ID is required")
        if not selected_spectra:
            errors.append("⚠️ Select at least one colour spectrum")
        if min_interval >= max_interval:
            errors.append("⚠️ Minimum interval must be less than maximum interval")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("✅ All required information provided")
            
            # Show experiment summary
            st.info(f"""
            **Experiment Summary:**
            - Participant: {participant_id} ({gender}, {age} years)
            - Spectra: {len(selected_spectra)} selected
            - Trials per spectrum: {trials_per_spectrum}
            - Total trials: {len(selected_spectra) * trials_per_spectrum}
            - Practice trial: {"Yes" if include_practice else "No"}
            - Estimated duration: {len(selected_spectra) * trials_per_spectrum * 1.5:.0f}-{len(selected_spectra) * trials_per_spectrum * 2:.0f} minutes
            """)
            
            if st.button("🎯 Start Experiment", type="primary", use_container_width=True):
                # Save configuration
                st.session_state.participant_id = participant_id
                st.session_state.gender = gender
                st.session_state.age = age
                st.session_state.selected_spectra = selected_spectra
                st.session_state.trials_per_spectrum = trials_per_spectrum
                st.session_state.total_steps = total_steps
                st.session_state.min_interval = min_interval
                st.session_state.max_interval = max_interval
                st.session_state.show_progress_bar = show_progress
                st.session_state.show_step_number = show_step_number
                st.session_state.experiment_start_time = datetime.now()
                
                # Create trial order
                spectra = get_spectra_list()
                trial_list = []
                for spectrum_name in selected_spectra:
                    for trial_num in range(trials_per_spectrum):
                        trial_list.append({
                            'spectrum_name': spectrum_name,
                            'start_color': spectra[spectrum_name][0],
                            'end_color': spectra[spectrum_name][1],
                            'trial_number': trial_num + 1
                        })
                
                if randomize_order:
                    random.shuffle(trial_list)
                
                st.session_state.spectra_order = trial_list
                
                # Decide next phase
                if include_practice:
                    st.session_state.phase = 'practice'
                    st.session_state.current_step = 0
                    st.session_state.current_trial_results = []
                    st.session_state.practice_start_color = "#FF0000"
                    st.session_state.practice_end_color = "#FFFF00"
                else:
                    st.session_state.phase = 'main'
                    st.session_state.current_trial = 0
                    st.session_state.current_step = 0
                
                st.rerun()
    
    with col2:
        st.subheader("ℹ️ About This Test")
        st.markdown("""
        This enhanced colour perception test measures:
        
        - **Detection accuracy**: Where you notice changes
        - **Reaction time**: How quickly you respond
        - **Sensitivity**: Subtle vs obvious changes
        - **Consistency**: Performance across trials
        
        Your data helps research on colour perception differences.
        """)

def render_practice_phase():
    """Render the practice trial phase"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("🎯 **PRACTICE TRIAL** - This trial is not recorded. Get familiar with the test!")
        
        # Run the colour display
        trial_complete = run_colour_trial(
            start_color=st.session_state.practice_start_color,
            end_color=st.session_state.practice_end_color,
            is_practice=True
        )
        
        if trial_complete:
            st.success("✅ Practice trial complete!")
            st.markdown("You detected **{}** colour changes during practice.".format(
                len(st.session_state.current_trial_results)))
            
            if st.button("▶️ Start Main Experiment", type="primary", use_container_width=True):
                st.session_state.phase = 'main'
                st.session_state.current_trial = 0
                st.session_state.current_step = 0
                st.session_state.current_trial_results = []
                st.session_state.false_alarms = 0
                st.rerun()
    
    with col2:
        st.subheader("💡 Tips")
        st.markdown("""
        - Watch the colour box carefully
        - Press button immediately when you see a change
        - Don't anticipate - wait for actual changes
        - Multiple detections per trial are okay
        """)

def render_main_experiment():
    """Render the main experiment phase"""
    
    current_trial_info = st.session_state.spectra_order[st.session_state.current_trial]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Trial header
        total_trials = len(st.session_state.spectra_order)
        st.markdown(f"### Trial {st.session_state.current_trial + 1} of {total_trials}")
        st.caption(f"Spectrum: **{current_trial_info['spectrum_name']}** (Trial #{current_trial_info['trial_number']})")
        
        # Run the colour display
        trial_complete = run_colour_trial(
            start_color=current_trial_info['start_color'],
            end_color=current_trial_info['end_color'],
            is_practice=False
        )
        
        if trial_complete:
            # Save trial results
            for result in st.session_state.current_trial_results:
                result['spectrum'] = current_trial_info['spectrum_name']
                result['trial_number'] = current_trial_info['trial_number']
                result['overall_trial'] = st.session_state.current_trial + 1
                st.session_state.all_results.append(result)
            
            # Check if more trials
            if st.session_state.current_trial + 1 < total_trials:
                st.success(f"✅ Trial {st.session_state.current_trial + 1} complete!")
                st.info(f"You detected **{len(st.session_state.current_trial_results)}** colour changes in this trial.")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("➡️ Next Trial", type="primary", use_container_width=True):
                        st.session_state.current_trial += 1
                        st.session_state.current_step = 0
                        st.session_state.current_trial_results = []
                        st.session_state.false_alarms = 0
                        st.rerun()
                
                with col_b:
                    if st.button("⏸️ Take a Break"):
                        st.info("Take your time. Click 'Next Trial' when ready to continue.")
            
            else:
                # All trials complete
                st.balloons()
                st.success("🎉 All trials complete! Excellent work!")
                
                if st.button("📊 View Results", type="primary", use_container_width=True):
                    st.session_state.phase = 'results'
                    st.session_state.experiment_end_time = datetime.now()
                    st.rerun()
    
    with col2:
        st.subheader("📊 Session Stats")
        # Current trial is in progress, so completed trials = current_trial (0-indexed means this many are done)
        completed_trials = st.session_state.current_trial
        st.metric("Trials Completed", f"{completed_trials}/{total_trials}")
        st.metric("Total Responses", len(st.session_state.all_results))
        
        if completed_trials > 0:
            avg_responses = len(st.session_state.all_results) / completed_trials
            st.metric("Avg Responses/Trial", f"{avg_responses:.1f}")

def run_colour_trial(start_color, end_color, is_practice):
    """Run a single colour trial and return whether it's complete"""
    
    # Check if trial is complete
    if st.session_state.current_step >= st.session_state.total_steps:
        return True
    
    # Get current colour
    current_rgb = interpolate_color(
        start_color,
        end_color,
        st.session_state.total_steps,
        st.session_state.current_step
    )
    current_hex = rgb_to_hex(current_rgb)
    
    # Display colour box
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
    
    # Progress indicator
    if st.session_state.show_progress_bar:
        progress = st.session_state.current_step / st.session_state.total_steps
        st.progress(progress)
        if st.session_state.show_step_number:
            st.caption(f"Step {st.session_state.current_step}/{st.session_state.total_steps}")
    
    # Detection button
    button_pressed = st.button(
        "👁️ I Detect a Change!",
        type="primary",
        use_container_width=True,
        key=f"detect_{st.session_state.current_step}_{st.session_state.current_trial}"
    )
    
    if button_pressed:
        button_press_time = time.time()
        reaction_time = calculate_reaction_time(st.session_state.last_step_change_time, button_press_time)
        
        # Record the result
        result = {
            "participant_id": st.session_state.participant_id,
            "gender": st.session_state.gender,
            "age": st.session_state.age,
            "step_number": st.session_state.current_step,
            "total_steps": st.session_state.total_steps,
            "percentage_complete": round((st.session_state.current_step / st.session_state.total_steps * 100), 2),
            "hex_code": current_hex,
            "rgb": f"({int(current_rgb[0])}, {int(current_rgb[1])}, {int(current_rgb[2])})",
            "reaction_time_ms": reaction_time,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        }
        
        st.session_state.current_trial_results.append(result)
        
        # Visual feedback
        if reaction_time and reaction_time < 200:
            st.warning(f"⚡ Very fast! ({reaction_time} ms) - Make sure you're detecting actual changes.")
            st.session_state.false_alarms += 1
        else:
            st.success(f"✓ Recorded: {current_hex} (RT: {reaction_time} ms)")
        
        time.sleep(0.2)
    
    # Auto-advance colour
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
    
    # Auto-refresh
    time.sleep(0.05)
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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trials", len(st.session_state.spectra_order))
    with col2:
        st.metric("Total Detections", len(st.session_state.all_results))
    with col3:
        avg_per_trial = len(st.session_state.all_results) / len(st.session_state.spectra_order) if st.session_state.spectra_order else 0
        st.metric("Avg Detections/Trial", f"{avg_per_trial:.1f}")
    with col4:
        st.metric("Duration", f"{duration_minutes:.1f} min")
    
    st.markdown("---")
    
    # Detailed results
    if st.session_state.all_results:
        st.subheader("📊 Detailed Results")
        
        df = pd.DataFrame(st.session_state.all_results)
        
        # Display participant info once (not repeated in table)
        st.info(f"**Participant:** {st.session_state.participant_id} | **Gender:** {st.session_state.gender} | **Age:** {st.session_state.age}")
        
        # Create a cleaner display version (remove redundant columns)
        display_df = df[[
            'overall_trial',
            'spectrum', 
            'trial_number',
            'step_number',
            'percentage_complete', 
            'hex_code', 
            'rgb',
            'reaction_time_ms'
        ]].copy()
        
        # Rename columns for better readability
        display_df.columns = [
            'Trial #',
            'Spectrum',
            'Rep',
            'Step',
            '% Complete',
            'Hex',
            'RGB',
            'RT (ms)'
        ]
        
        # Format percentage to 1 decimal place
        display_df['% Complete'] = display_df['% Complete'].apply(lambda x: f"{x:.1f}%")
        
        # Format reaction time to integer
        display_df['RT (ms)'] = display_df['RT (ms)'].apply(lambda x: f"{int(x)}" if pd.notna(x) else "—")
        
        # Show cleaner DataFrame with color coding option
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.caption("📋 **Detection Events** (showing only relevant columns)")
        with col_b:
            color_by_trial = st.checkbox("Color by trial", value=False, key="color_trials")
        
        if color_by_trial:
            # Add styling
            def highlight_trials(row):
                trial_num = row['Trial #']
                colors = ['background-color: #1f2937', 'background-color: #374151']
                return [colors[trial_num % 2]] * len(row)
            
            styled_df = display_df.style.apply(highlight_trials, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(display_df, use_container_width=True)
        
        st.caption("💡 Full data with all columns available in CSV/JSON export below")
        
        # Statistical summary
        st.subheader("📉 Statistical Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Detection Points**")
            st.write(f"- Mean: {df['percentage_complete'].mean():.1f}%")
            st.write(f"- Median: {df['percentage_complete'].median():.1f}%")
            st.write(f"- Std Dev: {df['percentage_complete'].std():.1f}%")
            st.write(f"- Range: {df['percentage_complete'].min():.1f}% - {df['percentage_complete'].max():.1f}%")
        
        with col2:
            st.markdown("**Reaction Times**")
            rt_data = df[df['reaction_time_ms'].notna()]['reaction_time_ms']
            if len(rt_data) > 0:
                st.write(f"- Mean: {rt_data.mean():.0f} ms")
                st.write(f"- Median: {rt_data.median():.0f} ms")
                st.write(f"- Std Dev: {rt_data.std():.0f} ms")
                st.write(f"- Range: {rt_data.min():.0f} - {rt_data.max():.0f} ms")
        
        # Breakdown by spectrum
        st.subheader("🎨 Performance by Spectrum")
        spectrum_summary = df.groupby('spectrum').agg({
            'percentage_complete': ['count', 'mean', 'std'],
            'reaction_time_ms': 'mean'
        }).round(2)
        spectrum_summary.columns = ['Detections', 'Mean % Detected', 'Std Dev %', 'Mean RT (ms)']
        
        # Format the display
        spectrum_summary['Mean % Detected'] = spectrum_summary['Mean % Detected'].apply(lambda x: f"{x:.1f}%")
        spectrum_summary['Std Dev %'] = spectrum_summary['Std Dev %'].apply(lambda x: f"{x:.1f}%")
        spectrum_summary['Mean RT (ms)'] = spectrum_summary['Mean RT (ms)'].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "—")
        
        st.dataframe(spectrum_summary, use_container_width=True)
        
        # Download options
        st.markdown("---")
        st.subheader("💾 Export Data")
        
        st.info("📌 **Note:** Exports contain ALL columns including participant info in every row (ideal for statistical analysis)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export - includes ALL original columns
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Data (CSV)",
                data=csv,
                file_name=f"colour_perception_{st.session_state.participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption(f"✓ Complete dataset: {len(df)} rows × {len(df.columns)} columns")
        
        with col2:
            # Summary export
            summary_data = {
                'participant_info': {
                    'id': st.session_state.participant_id,
                    'gender': st.session_state.gender,
                    'age': st.session_state.age,
                    'experiment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'experiment_config': {
                    'total_trials': len(st.session_state.spectra_order),
                    'gradient_steps': st.session_state.total_steps,
                    'interval_range': f"{st.session_state.min_interval}-{st.session_state.max_interval}s"
                },
                'performance_summary': {
                    'total_detections': len(st.session_state.all_results),
                    'mean_percentage': round(df['percentage_complete'].mean(), 2),
                    'median_percentage': round(df['percentage_complete'].median(), 2),
                    'std_percentage': round(df['percentage_complete'].std(), 2),
                    'mean_rt_ms': round(rt_data.mean(), 2) if len(rt_data) > 0 else None,
                    'duration_minutes': round(duration_minutes, 2)
                }
            }
            summary_json = json.dumps(summary_data, indent=2)
            st.download_button(
                label="📄 Download Summary (JSON)",
                data=summary_json,
                file_name=f"summary_{st.session_state.participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            st.caption("✓ Aggregated statistics only")
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Experiment", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()