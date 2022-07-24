export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-w5zvh1wa.us', // the auth0 domain prefix
    audience: 'drink', // the audience set for the auth0 app
    clientId: 'Pj3Z5vQBrK0k171OipbjXNy9ytx9VfJz', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:8100', // the base url of the running ionic application. 
  }
};
// https://dev-w5zvh1wa.us.auth0.com/authorize?audience=drink&response_type=token&client_id=Pj3Z5vQBrK0k171OipbjXNy9ytx9VfJz&redirect_uri=http://127.0.0.1:8100