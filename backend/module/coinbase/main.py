# this code will require proxies for every time an email is sent
# yet to be implemnted but will required
# update(v2) will have this, and kraken / google subscription 
import tls_client

def coinbase_bytes(email):
     
     session = tls_client.Session(
          client_identifier="chrome_120"
     )

     url = (
          "https://www.coinbase.com/graphql/query?&operationName=emailOnlyUserApiMutation"
     )

     headers = {
          "accept": "multipart/mixed;deferSpec=20220824, application/json",
          "accept-encoding": "gzip, deflate, br, zstd",
          "accept-language": "en",
          "content-type": "application/json",
          "origin": "https://www.coinbase.com",
          "referer": "https://www.coinbase.com/bytes",
          "sec-fetch-site": "same-origin",
          "sec-fetch-mode": "cors",
          "user-agent": (
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/120.0.0.0 Safari/537.36"
          ),
          "x-cb-client": "CoinbaseWeb",
          "x-cb-version": "2021-01-11",
          "x-cb-platform": "web",
          "x-cb-project-name": "consumer",
          "x-cb-pagekey": "bytes",
          "x-cb-device-id": "6f136e4a-e584-43d1-96ba-e2002eb9694d",
          "x-cb-is-logged-in": "false",
          "x-cb-user-id": "unknown",
          "x-cb-session-uuid": "66d3b3d6-8aa8-44c1-8dc3-98f5be945de9",
          "x-cb-version-name": "ad6b3b5b844630ea9659cffb25c1007a47233907"
     }

     payload = {
          "query": (
               "mutation emailOnlyUserApiMutation("
               "$input:SubscribeEmailOnlyUserInput!"
               "){subscribeEmailOnlyUser(input:$input)"
               "{__typename,...on SubscribeEmailOnlyUserSuccess{dummy},"
               "...on GenericError{message}}}"
          ),
          "operationName": "emailOnlyUserApiMutation",
          "variables": {
               "input": {
                    "email": email,
                    "countryCode": "US",
                    "locale": "en",
                    "currency": "USD",
                    "productId": "bytes_newsletter",
                    "subscribeMetadata": {}
               }
          }
     }

     response = session.post(
          url,
          headers=headers,
          json=payload
     )

     if response.status_code == 200:
          print(
               "sent email!"
          )
          print(
               response.json()
          )
     else:
          raise Exception(
               f"error: {response.status_code}"
          )
