# --- Rest of your app code ---
import itertools
import json
import os
import pathlib
import traceback

import streamlit as st
import streamlit.components.v1 as components


from version import __version__


_debug = False

# sys.path.append(os.path.dirname(__file__)) # This crashes the app on Streamlit Cloud!

# Fix the checkbox issue by adding a unique key
def show_colors(key=""):
    global c1, c2, c1inner, c2inner, selected_scheme, custom_input, color, col_left, col_center, col_right
    # Color scheme (existing code)...
    c1, c2, c3 = st.columns([1, 1, 10])
    container = st.container()
    with container:
        margin, left, c1inner, c2inner = st.columns([1, 1, 5, 5])
        with margin:
            st.markdown("**Color Scheme**")
        with left:
            show_preview = st.checkbox(
                "Show Preview", value=False, key=f"show_preview_{key}"
            )  # Added a unique key using the provided `key` parameter
        with c1inner:
            key = f"color_scheme_{key}"
            selected_scheme = st.selectbox(
                "Choose a predefined scheme",
                [scheme["name"] for scheme in colors],
                key=key,
                help="Select a color scheme to use. You can also enter custom colors.",
            )
        with c2inner:
            key = f"color_scheme_custom_{key}"
            custom_input = st.text_input(
                "Or enter color names or custom hex codes (comma-separated)",
                key=key,
                help="e.g., 'red, green, blue' is the same as '#FF0000, #00FF00, #0000FF'",
            )
    if custom_input.strip():
        color = custom_input
        preview_colors = [c.strip() for c in custom_input.split(",") if c.strip()]
    else:
        color = selected_scheme
        preview_colors = next(
            scheme["colors"] for scheme in colors if scheme["name"] == selected_scheme
        )
    preview_widgets = _build_color_previews(preview_colors)
    # Show color preview if selected
    if show_preview and preview_colors:
        col_left, col_center, col_right = st.columns([1, 1, 10])
        with col_left:
            st.markdown(" ")
        if selected_scheme == "Complementary":
            with col_center:
                st.markdown("*Preview*")
            for i in range(0, len(preview_colors), 2):
                pair = preview_colors[i: i + 2]
                col_left, col_center, col_right = st.columns(3)
                preview_widgets = _build_color_previews(pair)
                if len(preview_widgets) == 2:
                    col_center.markdown(preview_widgets[0], unsafe_allow_html=True)
                    col_right.markdown(preview_widgets[1], unsafe_allow_html=True)
                else:
                    col_center.markdown(preview_widgets[0], unsafe_allow_html=True)
        else:
            with col_center:
                st.write("*Preview*")
            preview_colors = _build_color_previews(preview_colors)
            col_right.markdown(
                """
                <div style='display:flex; flex-wrap:wrap; gap:4px;'>
                """
                + "".join(preview_colors)
                + """
                </div>
                """,
                unsafe_allow_html=True,
            )

try:
    # Must be the first Streamlit command!
    st.set_page_config(
        page_title=f"Prompt Forge {__version__}",
        layout="wide"
    )

    # st.write("Secrets available:", list(st.secrets.keys()))

    # from dotenv import load_dotenv

    # api_key = None
    # try:
    #     # Try Streamlit secrets first
    #     api_key = st.secrets["OPENAI_API_KEY"]
    #     # print("Using Streamlit secrets API key.") # Add for debugging if needed
    # except (KeyError, AttributeError):
    #     # print("Streamlit secrets not found, trying .env.") # Add for debugging if needed
    #     # Fallback to .env for local development
    #     load_dotenv()
    #     api_key = os.getenv("OPENAI_API_KEY")
    #
    # if not api_key:
    #     st.error("OpenAI API key not found. Please set it in Streamlit secrets or .env file.")
    #
    # try:
    #     client = openai.OpenAI(api_key=api_key)
    #     # Perform a simple test call maybe? Or just proceed.
    #     # client.models.list() # Example test - might cost a tiny bit
    # except Exception as e:
    #     st.error(f"Failed to initialize OpenAI client: {e}")
    #     st.stop()

    # --- Rest of your app code using 'client' ---

    # load_dotenv() # Loads variables from .env file


    import base64

    # ──────────────────────────────────────────
    # Helper Functions
    def _build_color_previews(colors: list[str]) -> list[str]:
        """
        Create tiny coloured squares for each supplied hex code.

        Parameters
        ----------
        colors : list[str]
            Hex strings such as '#ff7700'.

        Returns
        -------
        list[str]
            HTML snippets ready to be rendered with `unsafe_allow_html=True`.
        """
        return [
            f'''
            <div style="
                display:inline-block;
                width:40px;
                height:40px;
                margin:4px;
                border-radius:4px;
                border:1px solid #666;
                background:{hexcode};
            "></div>
            '''.strip()
            for hexcode in colors
        ]

    def copy_button(text: str, label: str = "Copy", key=None):
        """
        Create a button that copies text to the clipboard using JavaScript.

        Additionally, triggers an st.success message on successful click.
        """
        button_id = f"copy-button-{key}" if key else "copy-button"
        session_key = f"copy-success-{key}"  # Unique key to manage copy state

        # Check if the success message should be displayed
        if f"{session_key}" not in st.session_state:
            st.session_state[session_key] = False

        # If the state for success is True, display an st.success message
        if st.session_state[session_key]:
            st.success("Prompt copied to clipboard!")
            # Reset state after displaying the message
            st.session_state[session_key] = False

        # Custom HTML + JavaScript for the button
        custom_html = f"""
        <div>
            <button id="{button_id}" style="
                border-radius: 4px;
                background-color: #f0f2f6;
                color: #262730;
                padding: 0.35em 1em;
                font-size: 0.875rem;
                border: 1px solid #e6e9ef;
                cursor: pointer;
            ">
                📋 {label}
            </button>
            <script>
                const button = document.getElementById("{button_id}");
                button.addEventListener("click", () => {{
                    navigator.clipboard.writeText({text!r}).then(() => {{
                        // Inform Streamlit backend that copy was successful
                        window.parent.postMessage({{'isCopied': true, 'key': '{session_key}' }}, "*");
                    }}).catch(err => {{
                        alert("Failed to copy: " + err);
                    }});
                }});
            </script>
        </div>
    """

        # Handle postMessage callback from JavaScript to Streamlit
        components.html(
            f"""
        <script>
            window.addEventListener("message", (event) => {{
                if (event.data.isCopied && event.data.key === '{session_key}') {{
                    fetch('/_stcore/{session_key}');
                }}
            }});
        </script>
        """ + custom_html,
            height=50,
        )


    # Add this in an app initialization section to persist request handling
    @st.cache_data
    def handle_js_backend():
        """
        Simulate communication between JavaScript and Streamlit backend
        to trigger `st.success` message for copy.
        """
        session_keys = [key for key in st.session_state if "copy-success-" in key]
        for session_key in session_keys:
            def reset_copy_state(key=session_key):
                """Reset state after a short delay"""
                st.session_state[key] = True
            st.session_state[session_key] = False

    # Call to handle JavaScript backend communication
    handle_js_backend()


    # columns for banner + content
    col_left, col_center = st.columns([2, 7])

    with col_left:
        banner_path = pathlib.Path("assets/robo-generate.png")
        img_b64 = base64.b64encode(banner_path.read_bytes()).decode()
        st.markdown(f"""
          <style>
            .fixed-banner {{ position:fixed; top:0; left:0; width:25%; padding:5px;
                            margin:0; border-radius:5px;
                            background:transparent; z-index:9999; text-align:center; }}
            .block-container {{ padding-top:120px; }}
          </style>
          <div class="fixed-banner">
            <img src="data:image/png;base64,{img_b64}"
                    alt="Prompt Forge Banner"
                    title="Created with ChatGPT (ironically!) 😁"
                 style="width:60%; height:auto; margin:0 auto;">
          </div>
        """, unsafe_allow_html=True)

    with col_center:
        col_left, col_center, col_right = st.columns([1, 2, 1])  # Adjust column widths for centering

        def load_json(name):
            try:
                return json.load(open(os.path.join("data", f"{name}.json")))
            except FileNotFoundError:
                return []

        artists   = load_json("artists")
        styles    = load_json("styles")
        mediums   = load_json("mediums")
        moods     = load_json("moods")
        lighting  = load_json("lighting")
        colors    = load_json("colors")

        # Persistent header shown at the top, always visible
        st.markdown(
            f"""
            <div style="text-align:center; font-size: 28px; font-weight: bold; color: #1f2937; margin-top: 50px;">
                Prompt Forge v{__version__}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <style>
                .block-container {
                    padding-top: 0px;
                    padding-bottom: 0px;
                    padding-left: 0px;
                    padding-right: 0px;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Update tabs to include the "Documentation" tab
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Single Prompt", "🌀 Batch Mode", "🛠️ Edit Lists", "📖 Documentation"])

        #
        # === Tab 1: Single Prompt ===
        #
        with tab1:
            st.header("Build a Single Prompt")
            # Examples of adding explanatory help text to UI elements
            col1, col2, col3 = st.columns([1,1,1])

            with col1:
                # Text Input
                subject = st.text_input(
                    "Subject",
                    help="Enter the main subject or focus of your prompt. E.g., dragon, spaceship."
                )
            with col2:
                # Selectbox
                mood = st.multiselect(
                    "Mood",
                    options=moods,
                    default=["Happy", "Playful"],
                    help="Select the mood you want to convey in your image. E.g., calm, joyful, ominous."
                )

            with col3:
                # Multiselect
                styles_sel = st.multiselect(
                    "Styles",
                    options=styles,
                    default=[s for s in ["Cyberpunk", "Fantasy"] if s in styles],
                    help="Select one or more artistic styles to influence the image's appearance."
                )

            with col1:
                lighting_sel = st.selectbox(
                    "Lighting",
                    lighting,
                    help="Choose a lighting style or scene that best matches your prompt."
                )

            with col2:
                mediums_sel = st.multiselect(
                    "Mediums",
                    options=mediums,
                    default=[m for m in ["Digital Art", "3D render"] if m in mediums],
                    help="Choose the medium to define whether the image should look like a painting, 3D render, etc."
                )

            with col3:
                artists_sel = st.multiselect("Artists (by)", options=artists,
                                             default=[a for a in ["Moebius", "Basil Wolverton"] if a in artists],
                                             help="Select one or more artists to influence the image's style.")

            show_colors("single")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                version      = st.selectbox("Model Version (--v)", ["7","6","5.2","5.1","5","4"], help="Select the MidJourney model version to use.")
            with col2:
                aspect       = st.selectbox("Aspect Ratio (--ar)", ["1:1","16:9","4:5","2:3","3:2","9:16"], help="Select the aspect ratio for the image.")
            with col3:
                negative     = st.text_input("Negative Prompt (--no)", help="Exclude these terms.")

            c1, c2 = st.columns(2)
            with c1:
                # Sliders
                stylize = st.slider(
                    "Stylize (--s)",
                    min_value=0,
                    max_value=1000,
                    value=250,
                    step=1,
                    help="Higher values make the image more artistic. Lower values emphasize realism."
                )
            with c2:
                chaos = st.slider(
                    "Chaos (--chaos)",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=1,
                    help="Higher values create more random and unexpected results in the generated image."
                )
            with c1:
                stop         = st.slider(
                    "Stop (--stop)",
                    min_value=0, max_value=100, value=100, step=1,
                    help="Stop at this percentage of completion.",
                    key="stop"
                )
            with c2:
                weirdness    = st.slider(
                    "Weirdness (--weird)",
                    min_value=0, max_value=3000, value=0, step=1,
                    help="Adjust how ‘weird’ the output should be",
                    key="weirdness"
                )
            with col2:
                seed         = st.number_input("Seed (--seed)", min_value=0,   max_value=999999999, value=0, help="Random seed for reproducibility.")
            with col3:
                quality      = st.selectbox("Quality (--q)",  options=[" ", 0.25,0.5,1,2], help="Higher quality = longer render time.")

            marginl, col1, col2, col3, col4, marginr = st.columns([1, 1, 1, 1, 1, 1])
            with col1:
                tile         = st.checkbox("Tile (--tile)",  help="Generate a tileable image")
            with col2:
                video        = st.checkbox("Video (--video)", help="Generate a short video preview")
            with col3:
                uplight      = st.checkbox("Uplight (--uplight)", help="Use the light upscaler")
            with col4:
                upbeta       = st.checkbox("Upbeta (--upbeta)",   help="Use the beta upscaler")

            # Build the prompt string
            parts = [subject]
            if mood:
                parts += [f"{m}" for m in mood]
            parts += mediums_sel
            if styles_sel:
                parts += [f"{s}" for s in styles_sel]
            parts += [f"by {a}" for a in artists_sel]

            if color:
                if isinstance(color, str):
                    parts.append(color)
                else:
                    parts += [f"#{c}" for c in color]
            if lighting_sel:
                parts.append(lighting_sel)
            if negative:
                parts.append(f"--no {negative}")
            if isinstance(stylize, (int, float)) and stylize > 0:
                parts.append(f"--s {stylize}")
            if isinstance(chaos, (int, float)) and chaos > 0:
                parts.append(f"--chaos {chaos}")
            if isinstance(weirdness, (int, float)) and weirdness > 0:
                parts.append(f"--weird {weirdness}")
            if isinstance(quality, (int, float)) and quality > 0:
                parts.append(f"--q {quality}")
            if seed:
                parts.append(f"--seed {seed}")
            if isinstance(stop, (int, float)) and stop < 100:
                parts.append(f"--stop {stop}")
            if tile:    parts.append("--tile")
            if video:   parts.append("--video")
            if uplight: parts.append("--uplight")
            if upbeta:  parts.append("--upbeta")

            # version & aspect always last
            parts.append(f"--v {version}")
            parts.append(f"--ar {aspect}")

            final = " ".join(filter(None, parts))
            # Text area for output
            final = st.text_area(
                "Final Prompt",
                final,
                height=120,
                key="final_prompt",
                help="This is the final generated prompt. Copy it for use with MidJourney."
            )

            col_left, col1, col2, col_right = st.columns([1, 3, 3, 1])
            with col1:
                copy_button(
                    text=final,
                    label="Copy Prompt",
                    key="copy_single_prompt",
                )
            with col2:
                st.download_button(
                    "📥 Download Prompts as TXT",
                    data=final,
                    file_name="mj_prompt.txt",
                    key="single_prompt_download",
                )

        #
        # === Tab 2: Batch Mode ===
        #
        with tab2:
            st.header("Batch Prompt Generator", help="Title section for batch prompt generation.")
            st.markdown("Enter comma-separated values for batch combination:", help="Instructions for batch input format.")

            col1, col2, col3 = st.columns(3)
            with col1:
                subjects = st.text_input(
                    "Subjects",
                    "robot, dragon, astronaut",
                    help="Enter comma-separated subjects for prompts."
                )
            with col2:
                moods_batch = st.multiselect(
                    "Moods",
                    moods,
                    default=["Serene", "Dystopian", "Joyful"],
                    key="moods_batch",
                    help="Select moods to convey in the prompts."
                )
            with col3:
                styles_batch = st.multiselect(
                    "Styles",
                    styles,
                    default=["Cyberpunk", "Fantasy"],
                    key="styles_batch",
                    help="Select artistic styles to influence the appearance of the prompts."
                )
            with col1:
                lightings_batch = st.multiselect(
                    "Lighting",
                    lighting,
                    default=["Cinematic lighting", "Golden hour"],
                    key="lightings_batch",
                    help="Choose lighting effects for the prompts."
                )
            with col2:
                mediums_batch = st.multiselect(
                    "Mediums",
                    mediums,
                    default=[m for m in ["Digital Art", "3D render"] if m in mediums],
                    key="mediums_batch",
                    help="Select mediums to define how the image should look, e.g., painting or 3D render."
                )
            with col3:
                artists_batch = st.multiselect(
                    "Artists",
                    artists,
                    default=["Greg Rutkowski", "Beeple"],
                    key="artists_batch",
                    help="Select artists to influence the artistic style of the prompts."
                )
            show_colors("batch")

            with col1:
                version_b = st.selectbox(
                    "Model Version (--v)",
                    ["7", "6", "5.2", "5.1", "5", "4"],
                    key="ver2",
                    help="Select the MidJourney model version for batch prompts."
                )
            with col2:
                aspect_b = st.selectbox(
                    "Aspect Ratio (--ar)",
                    ["1:1", "16:9", "4:5", "2:3", "3:2", "9:16"],
                    key="ar2",
                    help="Choose the aspect ratio for the generated outputs."
                )
            with col3:
                negative_b = st.text_input(
                    "Negative Prompt (--no)",
                    key="neg_b",
                    help="Input keywords to exclude from the prompt generation."
                )
            c1, c2 = st.columns(2)
            with c1:
                stylize_b = st.slider(
                    "Stylize (--s)",
                    min_value=0, max_value=100, value=250, step=1,
                    key="stylize_b",
                    help="Adjust stylization level for the generated images."
                )
            with c2:
                chaos_b = st.slider(
                    "Chaos (--chaos)",
                    min_value=0, max_value=100, value=0, step=1,
                    key="chaos_b",
                    help="Control randomness level of the outputs; higher values generate more unexpected results."
                )
            with c1:
                stop_b = st.slider(
                    "Stop (--stop)",
                    min_value=0, max_value=100, value=100, step=1,
                    help="Specify the percentage of completion at which the processing should stop."
                )
            with c2:
                weirdness_b = st.slider(
                    "Weirdness (--weird)",
                    min_value=0, max_value=3000, value=0, step=1,
                    key="weirdness_b",
                    help="Adjust the level of weirdness in the generated images."
                )
            with col1:
                quality_b = st.selectbox(
                    "Quality (--q)",
                    [0.25, 0.5, 1, 2],
                    index=2,
                    key="quality_b",
                    help="Set the quality of the image render; higher values result in better quality but longer render time."
                )
            with col2:
                seed_b = st.number_input(
                    "Seed (--seed)",
                    min_value=0,
                    max_value=999999999,
                    value=0,
                    key="seed_b",
                    help="Set a random seed value for reproducible results."
                )
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                tile_b = st.checkbox(
                    "Tile (--tile)",
                    key="tile_b",
                    help="Enable tile generation to produce seamless, repeating patterns."
                )
            with col2:
                video_b = st.checkbox(
                    "Video (--video)",
                    key="video_b",
                    help="Generate a video preview of the image creation process."
                )
            with col3:
                uplight_b = st.checkbox(
                    "Uplight (--uplight)",
                    key="uplight_b",
                    help="Use the light version of the image upscaler."
                )
            with col4:
                upbeta_b = st.checkbox(
                    "Upbeta (--upbeta)",
                    key="upbeta_b",
                    help="Enable beta upscaling during image enhancement."
                )
            with col3:
                auto_generate = st.checkbox(
                    "Auto Generate",
                    value=True,
                    key="auto_generate",
                    help="Automatically generate batch prompts without needing manual intervention."
                )

            prompts = []

            # make flags function
            def make_flags(v, ar, neg, s, ch, q, se, stp, tile, vid, upl, upb, w):
                flags = [f"--v {v}", f"--ar {ar}"]

                if neg:
                    flags.append(f"--no {neg}")
                if s:
                    flags.append(f"--s {s}")
                # only add chaos if > 0
                if isinstance(ch, (int, float)) and ch > 0:
                    flags.append(f"--chaos {ch}")
                if q:
                    flags.append(f"--q {q}")
                if se:
                    flags.append(f"--seed {se}")
                if isinstance(stp, (int, float)) and stp < 100:
                    flags.append(f"--stop {stp}")

                if tile:
                    flags.append("--tile")
                if vid:
                    flags.append("--video")
                if upl:
                    flags.append("--uplight")
                if upb:
                    flags.append("--upbeta")

                # only add weirdness if > 0
                if isinstance(w, (int, float)) and w > 0:
                    flags.append(f"--weird {w}")

                return " ".join(flags)

            def generate_batch():
                combos = list(itertools.product(
                    [x.strip() for x in subjects.split(",") if x.strip()],
                    moods_batch, lightings_batch,
                    styles_batch, mediums_batch, artists_batch
                ))
                for combo in combos:
                    s,m,l,stl,med,a = combo
                    base = f"{s}, {m}, {l}, {med}, {stl}, by {a}"
                    flags = make_flags(
                        version_b, aspect_b,
                        negative_b, stylize_b, chaos_b, quality_b,
                        seed_b, stop_b, tile_b, video_b, uplight_b, upbeta_b, weirdness
                    )
                    prompts.append(f"{base} {flags}")

            if not auto_generate:
                if st.button("Generate", key="gen_btn"):
                    generate_batch()
            else:
                generate_batch()

            if prompts:
                batch_prompts_text = "\n".join(prompts)

                # Text area for generated prompts
                st.text_area("Generated Prompts", batch_prompts_text, height=300)

                col_left, col1, col2, col_right = st.columns([1, 3, 3, 1])
                with col1:
                    # Copy Button
                    copy_button(
                        text=batch_prompts_text,
                        label="Copy Prompts",
                        key="copy_batch_prompts"
                    )

                with col2:
                    # Download Button
                    st.download_button(
                        "📥 Download Prompts as TXT",
                        data=batch_prompts_text,
                        file_name="batch_prompts.txt"
                    )

        #
        # === Tab 3: Edit Lists ===
        #
        with tab3:
            st.header("Edit Lists")
            st.markdown("* This will not update the GitHub JSON files *")

            for name, lst in [
                ("artists.json",  sorted(artists)),
                ("styles.json",   sorted(styles)),
                ("mediums.json",  sorted(mediums)),
                ("moods.json",    sorted(moods)),
                ("lighting.json", sorted(lighting)),
                ("colors.json",   sorted(colors, key=lambda s: s["name"]))
            ]:
                st.subheader(name.replace(".json","").title())
                st.text_area(name, json.dumps(lst, indent=2), height=150)

        # === Tab 4: Documentation ===
        with tab4:
            try:
                # Load the README.md content
                readme_path = pathlib.Path("README.md")
                if readme_path.exists():
                    readme_content = readme_path.read_text(encoding="utf-8")
                    # Display README.md as Markdown
                    st.markdown(readme_content, unsafe_allow_html=True)
                else:
                    st.error("README.md file not found. Please ensure the file is available in the project directory.")
            except Exception as e:
                st.error("Error loading documentation:")
                st.code(traceback.format_exc())

    # ──────────────────────────────────────────
    # Footer
    # ──────────────────────────────────────────
    st.markdown(
        """
        <style>
            /* Hide streamlit's default footer */
            footer {visibility: hidden;}

            /* Custom footer */
            .custom-footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                text-align: center;
                font-size: 1.0rem;
                padding: 0.5rem 0;
                background: rgba(220, 220, 220, 0.85);
            }
        </style>

        <div class="custom-footer">
            🚀 View the project
            <a href="https://github.com/lelandg/promptforge" target="_blank">
                PromptForge on GitHub
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # result = subprocess.run(['pip', 'list'], stdout=subprocess.PIPE)
    # st.text(result.stdout.decode('utf-8'))

    if _debug:
        with col_center:
            st.write("App started ✅")

except Exception as e:
    st.error("Startup error:")
    st.code(traceback.format_exc())