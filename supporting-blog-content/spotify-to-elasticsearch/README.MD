# Spotify to Elasticsearch

What does it do?

- It works with the spotify API to retrieve metadata.
- It imports your Spotify Privacy export.
- It sends all your songs to an Elasticsearch Cluster for analyzing.

## Requirements

It uses the [Spotipy](https://spotipy.readthedocs.io/en/2.25.0/) library to connect and interact with Spotify API. Therefore you need to create your own Spotify Developer Account.

To minimize the strain on the Spotify API, we are creating a local `metadata_cache.json` file that stores all the unique songs ID + metadata retrieved. If you listen to a song twice, we will only ask the Spotify API once for the metadata.

This was tested and written with Python 3.13.

### Spotify data export

This can take up to 30 days. You will get a mail as soon as the download is ready.

1. Go to [Spotify Privacy](https://www.spotify.com/account/privacy/)
2. Scroll down and select: `Extended Streaming History` it is the right top one.
3. Click in the bottom `request data`
4. You will get a mail to validate that you want this data.
5. Wait until you receive a mail that your data is ready for download.

### Spotify developer account

We need a Spotify developer account otherwise we are not allowed to ask the API.

1. Go to [Spotify Developer](http://developer.spotify.com/)
2. In the top right corner `Log In`
3. Log In with your normal Spotify Account
4. In the top right corner, where the `Log In` button was, click on your name and select `Dashboard`
5. Click on `Create App`
6. Give it an App name like `Elasticsearch Wrapped`
7. Give it a description like `Reading metadata about songs for Elasticsearch`
8. Redirect URIs put `http://localhost:9100`
9. Under: `Which API/SDKs are you planning to use?`
   1. Select `Web API`
10. Accept the terms and conditions
11. In the top right corner select `Settings`
12. Copy `client ID` and `client secret`. (We pass this as parameters when we run the script)

### Elastic API Key & Elasticsearch URL

1. Log into your Elastic cluster [Elastic Cloud](https://cloud.elastic.co) and either do a serverless project or hosted deployment. (It works with On Premise or any other form of deployment as well)
2. Serverless, you would create an `Observability Project`
   1. Go to manage, click in the top right corner on: `Connection details` and mark down the `Elasticsearch URL`. Should look something like this `https://<project-name>-number.es.<region>`
   2. API Key (Please note that this will give the API key the same permissions you have, easiest and quickest)
      1. UI:
         1. Project Settings => Management => API keys => Create API Key => `spotify` as name. Copy the `endcoded` value. It will only be shown once.
      2. Developer Tools:

```json
POST _security/api_key
{
    "name": "spotify"
}
```

3. Hosted deployment:
   1. Go onto your deployment, or create a new one.
   2. Press the `copy endpoint` button for Elasticsearch.
   3. API Key:

```json
POST _security/api_key
{
    "name": "spotify"
}
```

> Note: If you want more fine grained control, this is the minimum the application needs:

<details>
    <summary> API Request </summary>

```json
POST _security/api_key
{
  "name": "spotify",
  "role_descriptors": {
    "spotify_history": {
      "cluster": [
        "monitor",
        "manage_ingest_pipelines"
      ],
      "indices": [
        {
          "names": [
            "spotify-history"
          ],
          "privileges": [
            "all"
          ],
          "field_security": {
            "grant": [
              "*"
            ],
            "except": []
          },
          "allow_restricted_indices": false
        }
      ],
      "applications": [],
      "run_as": [],
      "metadata": {},
      "transient_metadata": {
        "enabled": true
      }
    }
  }
}
```

</details>

## Executing

1. Place the extracted files from the zip folder into the `to_read` folder. It needs to be the JSON files directly and not the zip.
1. Execute `pip install -r requirements.txt` and install all the dependencies.
1. Just run in your favorite shell and it will execute and find all the files in the `to_read` folder.

```shell
python3 python/main.py \
--es-url "https://spotify.es....:443" \
--es-api-key "WFdNcE1KTU...==" \
--spotify-client-id "f972762..." \
--spotify-client-secret "74bcf5196b..." \
--user-name "philipp"
```

The `--user-name` is optional but helpful if you index the data of your friends and family as well. The field in Elastic is then called `user`

## Caveats

- It only works with songs. No support for videos, podcasts or anything else yet.
- If you restart it at any point, it will just index everything again and overwrite what is in there. It moves the finished file to the `processed` folder. Once a file is fully done, it won't be touched again unless you move it to the `to_read` folder again.
- The way I set the `_id` means that you can only listen to one artist per second.
- It will log the track for which it cannot find any metadata. That could be due to spotify changing the track ID, because it removed the album the track was part of.

## Kibana Dashboard

There is a prebuild dashboard available, you can import that through the saved objects in Kibana. It was built on 8.17.

![Kibana Dashboard Preview](kibana/dashboard.jpeg)
