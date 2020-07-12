from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import os
import json
from contextlib import closing
from tempfile import gettempdir

BUCKET_ROOT = 'https://unroutine-sequences.s3-us-west-2.amazonaws.com'

class AudioManager:
    def __init__(self):
        session = Session(aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
        self.polly = session.client('polly')
        self.s3 = session.client('s3')

    def getSequenceUrl(self, sequence, transitionsWithFoot, cw, startIdx, endIdx):
        # Check the sequence
        decoded = json.loads(sequence.audioFilesJson)
        fileNames = decoded['files']

        cwName = 'cw' if cw else 'ccw'
        seek = f'{sequence.id}_{cwName}_{startIdx}_{endIdx}'

        try:
            audioFileName = next(fileName for fileName in fileNames if fileName == seek)
        except:
            audioFileName = None

        if audioFileName is None:
            audioFileName = seek
            # create it in polly 
            filePath = self.createPollyFile(transitionsWithFoot, audioFileName)
            if filePath is None:
                return None

            # save to S3 
            try:
                response = self.s3.upload_file(filePath, 'unroutine-sequences', f'{audioFileName}.mp3', ExtraArgs={'ACL': 'public-read'})
            except ClientError as e:
                print(e)
                return None

            # save to json
            fileNames.append(audioFileName)
            sequence.audioFilesJson = json.dumps({'files': fileNames})
            sequence.save()

        return f'{BUCKET_ROOT}/{audioFileName}.mp3'

    def textFromTransition(self, transition):
        foot = 'Left' if transition.entry.foot == 'L' else 'Right'
        return f'{transition.move.name} to {foot} {transition.exit.name}'

    def createPollyFile(self, transitionsWithFoot, audioFileName):
        entry = transitionsWithFoot[0].entry
        foot = 'Left' if entry.foot == 'L' else 'Right'
        text = f'Start on {foot} {entry.name}. ' + ', '.join(map(self.textFromTransition, transitionsWithFoot))

        try:
            # Request speech synthesis
            response = self.polly.synthesize_speech(Text=text, OutputFormat="mp3",
                                                VoiceId="Joanna")
        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            print(error)
            return None
        
        # Access the audio stream from the response
        if "AudioStream" in response:
            # Note: Closing the stream is important because the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(gettempdir(), f'{audioFileName}.mp3')
        
                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    return None
        
            return output
        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")

        return None

 




