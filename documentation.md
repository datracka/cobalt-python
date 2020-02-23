# API endpoints

## `/api/login` [GET]

third party login using Github outputs access token

(internally server redirects to authentication server to proceed to authorization, who redirects to `/api/callback` later on)

## `/api/get_repositories` [GET]

### params

- access_token

Example: `"api/get_repositories?access_token=123123123123123"`

Run Job for retrieving repositories given a search


