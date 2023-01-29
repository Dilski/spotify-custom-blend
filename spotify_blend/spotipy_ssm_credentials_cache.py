from spotipy.cache_handler import CacheHandler
import boto3
import json


class SSMCacheHandler(CacheHandler):
    def __init__(self, param_name: str) -> None:
        super().__init__()
        self.ssm_client = boto3.client("ssm")
        self.param_name = param_name

    def get_cached_token(self):
        """
        Get and return a token_info dictionary object.
        """
        response = self.ssm_client.get_parameter(
            Name=self.param_name, WithDecryption=True
        )
        return json.loads(response["Parameter"]["Value"])

    def save_token_to_cache(self, token_info):
        """
        Save a token_info dictionary object to the cache and return None.
        """
        self.ssm_client.put_parameter(
            Name=self.param_name,
            Value=json.dumps(token_info),
            Type="SecureString",
            Overwrite=True,
        )
        return None
