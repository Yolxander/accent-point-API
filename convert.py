from openvoice_cli import tune_one

# Run tone-color transfer
tune_one(
    input_file="speech_original.wav",   # your input voice
    ref_file="voice_ref.wav",           # reference voice
    output_file="result.wav",           # output
    device="cpu"                        # Intel Mac -> CPU
)

print("Done! Check result.wav")
