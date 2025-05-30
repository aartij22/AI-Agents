
def pre_process_transcript(text):
    """
    Pre-processes or cleans the transcript to get rid of unnecessary items
    :param text: The file contents that needs to be pre-processed/cleaned
    Returns:
        String to be summarised that is passed along with the prompt
    """
    pass


def summarize_context(text) -> str:
    """
    Generates a structured summary of a meeting transcript.

    This function should be invoked when the user requests a summary of any meeting transcript.
    It processes the input text for a language model to produce a consistent output.

    This function is the default entry point for meeting transcript tasks.

    :param text: The raw/pre-processed text of the transcript to be summarized.
    :return: A formatted prompt string to be passed to the model for generating a summary.
    """

    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are provided with a meeting transcript.
    Your task is to generate minutes of meeting with all the crucial information. 
    Do not assume that the reader is aware of the details. Add any minute detail you think will be beneficial. 
    Do not alter any information or names.

    Organize the MoM in the following format - 
    Attendees: Participants involved
    Agenda: Include the motive/agenda of the scheduled meeting
    Points discussed: Include all essential points that were discussed along with the person name. Make sure to add all important terms.
    Blocker: Include this field only if a blocker exists
    Next steps: Follow up tasks

    Make sure to follow this template exactly.

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Meeting Transcript: {text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
