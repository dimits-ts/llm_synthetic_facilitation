import uuid
import os
import argparse

from sdl import annotation_io
from sdl.persona import LlmPersona
from sdl.file_utils import read_file


def generate_annotator_file(
    annotator_personas: list[LlmPersona], instructions: str, history_ctx_len: int
) -> annotation_io.LlmAnnotationData:
    """Generate an annotation configuration object from provided attributes.
    The object can then be used for IO operations or directly as input for a conversation.

    :param annotator_personas: a list of all personas in JSON/dict format, from which a random subset will be selected depending on num_users
    :type annotator_personas: list[LlmPersona]

    :return: An IO conversation configuration object which can be used for persistence, or as input for a conversation
    :rtype: conversation_io.LLMConvData
    """
    flattened_annotator_attributes = [
        " ".join(persona.to_attribute_list()) for persona in annotator_personas
    ]

    data = annotation_io.LlmAnnotationData(
        attributes=flattened_annotator_attributes,
        instructions=instructions,
        history_ctx_len=history_ctx_len,
    )
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Generate conversation configs using modular configuration files"
    )

    parser.add_argument(
        "--output_dir",
        required=True,
        help="Output directory for generated annotation config files",
    )
    parser.add_argument(
        "--persona_dir",
        required=True,
        help="Directory containing JSON files for LLM annotator personas",
    )
    parser.add_argument(
        "--instruction_path",
        required=True,
        help="Path to .txt file containing annotator instructions",
    )
    parser.add_argument(
        "--history_ctx_len",
        type=int,
        default=4,
        help="How many previous comments the annotator will remember.",
    )
    args = parser.parse_args()

    print("Reading input files...")
    persona_files = os.listdir(args.persona_dir)
    personas = [
        LlmPersona.from_json_file(os.path.join(args.persona_dir, persona_file))
        for persona_file in persona_files
    ]
    instructions = read_file(args.instruction_path)

    print("Processing...")
    annotation_config_file = generate_annotator_file(
        annotator_personas=personas,
        instructions=instructions,
        history_ctx_len=args.history_ctx_len,
    )

    print("Writing new annotation config file...")
    annotation_config_file.to_json_file(
        os.path.join(args.output_dir, str(uuid.uuid4()) + ".json")
    )
    print("File exported to " + args.output_dir)


if __name__ == "__main__":
    main()