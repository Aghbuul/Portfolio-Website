# Implementing API Keys: A Comprehensive Guide

## The Problem We Faced

We encountered a critical issue where the OpenAI API was rejecting our requests with a 401 error (Invalid API Key), despite having what appeared to be a valid API key. The root cause was an incorrect assumption about API key formats.

### Initial Problematic Code

```python
def get_api_key():
    api_key = environ.get('OPENAI_API_KEY')
    if api_key:
        # MISTAKE: Making assumptions about API key format
        if not api_key.startswith('sk-'):
            logger.error("API key does not start with 'sk-'")
        if len(api_key) != 51:  # MISTAKE: Hardcoding expected length
            logger.error(f"API key length ({len(api_key)}) is not standard")
    return api_key
```

### The Fixed Code

```python
def get_api_key():
    api_key = environ.get('OPENAI_API_KEY')
    logger.debug("Checking environ.get() for API key...")
    if api_key:
        # Simply log the presence of the key without making format assumptions
        logger.debug("Found API key in environ.get()")
        logger.debug(f"API key found - length: {len(api_key)}")
        logger.debug(f"API key prefix: {api_key.split('-')[0] if '-' in api_key else 'unknown'}")
    return api_key
```

## Key Lessons Learned

1. **Never Make Assumptions About API Key Formats**
   - API key formats can change
   - Different API providers use different formats
   - Even the same provider might have different key formats for different services or tiers
   - Our specific case: We assumed all OpenAI keys start with `sk-` and have length 51, but they now have keys starting with `sk-proj-`

2. **Environment Variable Best Practices**
   - Use `.env` files for local development
   - Always load environment variables early in your application
   - Use `python-dotenv` or similar libraries to manage environment variables
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Load at application startup
   ```

3. **Proper Error Handling**
   - Log API errors with sufficient detail
   - Include error types and messages in logs
   - Don't mask or modify API error messages
   ```python
   try:
       client = OpenAI(api_key=api_key)
       response = client.some_endpoint()
   except Exception as e:
       logger.error(f"API Error: {str(e)}")
       logger.error(f"Error type: {type(e)}")
       logger.error(f"Error args: {e.args}")
   ```

4. **Testing API Keys**
   - Test API keys with a simple request before using them extensively
   - Include proper error messages for invalid keys
   - Log successful key validation
   ```python
   def test_api_key(api_key):
       try:
           client = OpenAI(api_key=api_key)
           # Make a simple test request
           test_response = client.moderations.create(input="test")
           return True
       except Exception as e:
           logger.error(f"API key validation failed: {e}")
           return False
   ```

## Implementation Checklist

1. **Environment Setup**
   - [ ] Create a `.env` file for local development
   - [ ] Add `.env` to `.gitignore`
   - [ ] Install `python-dotenv` or equivalent
   - [ ] Load environment variables at application startup

2. **API Key Management**
   - [ ] Store API keys in environment variables
   - [ ] Never hardcode API keys in source code
   - [ ] Don't make assumptions about key formats
   - [ ] Implement proper key rotation mechanisms

3. **Error Handling**
   - [ ] Implement comprehensive error logging
   - [ ] Handle API-specific errors appropriately
   - [ ] Provide meaningful error messages to users
   - [ ] Include debugging information in logs

4. **Security Best Practices**
   - [ ] Never log full API keys
   - [ ] Use HTTPS for all API communications
   - [ ] Implement rate limiting
   - [ ] Regular key rotation
   - [ ] Proper access control and key management

## Common Mistakes to Avoid

1. **Format Assumptions**
   - Don't assume key formats are fixed
   - Don't validate keys based on format
   - Let the API validate its own keys

2. **Error Handling**
   - Don't swallow errors without logging
   - Don't expose sensitive information in error messages
   - Don't continue processing with invalid keys

3. **Security**
   - Don't store API keys in version control
   - Don't share API keys in logs or error messages
   - Don't use production keys in development

4. **Implementation**
   - Don't hardcode API endpoints
   - Don't mix development and production keys
   - Don't forget to handle key rotation

## Testing API Keys

Always implement a proper testing strategy:

```python
def validate_api_key(api_key):
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        # Make a minimal test request
        test_response = client.moderations.create(input="test")
        
        # Log success without exposing key
        logger.info("API key validated successfully")
        return True
        
    except Exception as e:
        # Log failure without exposing key
        logger.error(f"API key validation failed: {type(e).__name__}")
        return False
```

## Conclusion

The key takeaway from our debugging session is to never make assumptions about API key formats or validation. Let the API provider handle key validation and focus on proper error handling and logging. This approach saves development time and prevents issues with changing API key formats or different key types. 