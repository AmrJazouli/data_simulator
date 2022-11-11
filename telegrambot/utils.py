import config
import requests
from boto3.dynamodb.conditions import Attr
from kafkaconsumer.consumer import KafkaConsumer
from dynamodb_config import dynamodb
import pickle
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


def download_model(url):
    """
        This function gets the deployed model from AWS
    :param url: AWS S3 bucket URL
    :return: .bin file with the model
    """
    try:
        response = requests.get(url).content
        return response
    except:
        return False


def get_data_dynamodb(device: str):
    """
        This function returns all documents on dynamodb from the given device based on an index
    :param device: The device name to filter the query by ['raspberry', 'pc1', 'pc2']
    :return: last element from the executed query, which is the last element loaded produced by the device
    """
    query_response = dynamodb.Table('sensors_data').scan(FilterExpression=Attr("device").eq(device),
                                                         IndexName="device-loading_datetime-index")
    # Return the last element loaded, with latest loading_datetime
    return query_response["Items"][-1]


class Predict:
    """
        Class that predicts whether a device will need technical intervention or not
    """

    def __init__(self, url_pc1=config.link_model_pc1, url_pc2=config.link_model_pc2,
                 url_rasb=config.link_model_raspberry):
        """
            Initialization of the class Predict
        :param url_pc1: URL for device PC1
        :param url_pc2: URL for device PC2
        :param url_rasb: URL for device Raspberry
        """
        self.pc1_model_url = url_pc1
        self.pc2_model_url = url_pc2
        self.rasb_model_url = url_rasb

        self.current_message = None

    def get_data_consumer(self, topic: str):
        """
            This function consumes data from the specified topic
        :return: last element from the executed query, which is the last element loaded produced by the device
        """
        KafkaConsumer().serializing_consumer.subscribe([topic])

        while True:
            try:
                msg = KafkaConsumer().serializing_consumer.poll(1.0)
                if msg is None:
                    continue

                message = msg.value()  # ¡¡ THE MESSAGE CONSUMED !! #
                if message is not None:
                    # Assign the message to make the prediction and store it in DynamoDb
                    self.current_message = message
                    print(f'[\n'
                          f'\tNew measure: \n'
                          f'\tuuid: {message.uuid}\n'
                          f'\tdevice: {message.device}\n'
                          f'\tloading_datetime: {message.loading_datetime}\n')
            except KeyboardInterrupt:
                break

        print('Closing the Consumer ...')
        KafkaConsumer().serializing_consumer.close()

    def predict_output(self, device: str):
        """
            This function predicts the output value whether the device will need technical intervention or not based on
            the last produced record from the device
        :param device: device name
        :return: last data record and prediction
        """
        url = ""
        data_input = []
        if device == "pc1":
            url = self.pc1_model_url
            logging.info("URL Device: PC1")
            self.get_data_consumer(topic=device)  # self.current_message contains current message consumed
            val = get_data_dynamodb(device)
            for i, elt in enumerate(config.pc1_features):
                for data in val:
                    if data == elt:
                        print(i, data, val[data])
                        data_input.append(float(val[data]))

        elif device == "pc2":
            url = self.pc2_model_url
            logging.info("URL Device: PC2")
            self.get_data_consumer(topic=device)  # self.current_message contains current message consumed
            val = get_data_dynamodb(device)
            for i, elt in enumerate(config.pc2_features):
                for data in val:
                    if data == elt:
                        print(i, data, val[data])
                        data_input.append(float(val[data]))

        elif device == "raspberry":
            url = self.rasb_model_url
            logging.info("URL Device: RASPBERRY")
            self.get_data_consumer(topic=device)  # self.current_message contains current message consumed
            val = get_data_dynamodb(device)
            for i, elt in enumerate(config.rasb_features):
                for data in val:
                    if data == elt:
                        print(i, data, val[data])
                        data_input.append(float(val[data]))
        else:
            logging.error("Wrong device provided.")

        # Download model from AWS S3 bucket
        model_raw = download_model(url)
        model = pickle.loads(model_raw)

        data = data_input

        # Make prediction based on the deployed model
        if device == 'pc2':
            prediction = model.predict([data_input + [0, 0]])
        else:
            prediction = model.predict([data_input])

        return data, prediction