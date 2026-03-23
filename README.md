Step 1 — Create the Lambda Function

Go to AWS Console → search Lambda → click it
Click "Create function"
Choose "Author from scratch"
Function name: health-calculator
Runtime: Python 3.12
Click "Create function"

You land on the function page. In the Code tab you see a file called lambda_function.py with a default hello world function.
Select all the code (Ctrl+A) → delete it → paste the entire lambda_function.py file I gave you above.
Click the orange Deploy button. Wait for the green success banner.

Step 2 — Test the Lambda
Still on the Lambda page, click the "Test" tab. Click "Create new test event", name it test1, and paste this as the body:
json{
  "requestContext": {"http": {"method": "POST"}},
  "body": "{\"weight_kg\":70,\"height_cm\":175,\"age\":25,\"gender\":\"male\",\"activity\":\"moderate\"}"
}
Click "Test". You should see a green result with BMI, calories, macros etc. If you see that — Lambda is working perfectly.

Step 3 — Create API Gateway

AWS Console → search API Gateway → click it
Click "Create API"
Choose "HTTP API" → click "Build"
Click "Add integration" → choose Lambda → select your health-calculator function
API name: health-calculator-api
Click "Next" → on the Routes page:

Method: POST
Resource path: /calculate


Click "Next" → "Next" → "Create"
On the next screen, copy the "Invoke URL" — it looks like https://abc123.execute-api.us-east-1.amazonaws.com


Step 4 — Update your HTML file
Open index.html. At the top of the <script> section, find this line:
javascriptconst API_URL = "https://YOUR-API-GATEWAY-URL/calculate";
Replace it with your actual URL like this (add /calculate at the end):
javascriptconst API_URL = "https://abc123.execute-api.us-east-1.amazonaws.com/calculate";
Save the file.

Step 5 — Deploy to S3 + CloudFront
Follow the exact same S3 + CloudFront steps from before — upload your updated index.html to S3, set the bucket policy, enable static hosting, create CloudFront distribution.
Once CloudFront is live, open your https://XXXX.cloudfront.net URL → enter your stats → hit Calculate → your Lambda runs the math and sends back the full results. Done!





=====================================================================if you got the some issue then do below things============================================================================================================
Fix the Default Root Object — 4 clicks
1.
You are already on the right page. Click the Edit button in the top-right of the Settings section (you can see it in your screenshot).
2.
Scroll down until you see a field called "Default root object". It is currently empty.
3.
Type exactly this into that field:
index.html
4.
Scroll to the bottom → click the orange "Save changes" button. CloudFront will re-deploy (another 1–2 min).



===============================================================================================================================================================
→
Fix CORS — click by click
Do this now
1.
In the left sidebar of API Gateway, click CORS (you can already see it listed — it's right below "Integrations" in your screenshot)
2.
Click the Configure button (or Edit if it already has settings)
3.
Fill in these exact values:
Access-Control-Allow-Origin
*
Access-Control-Allow-Headers
content-type
Access-Control-Allow-Methods
POST, OPTIONS
Access-Control-Max-Age
300
4.
Click Save — API Gateway will auto-redeploy in about 30 second
======================================================================================================================================================================
One more thing — Lambda invoke permission
Also check
→
Your screenshot shows "Invoke permissions" section — this means API Gateway may not have permission to call your Lambda yet. You need to add it manually.
Fix
Go to AWS Lambda → open health-calculator → click Configuration tab → click Permissions → scroll to Resource-based policy statements → click Add permissions
Select
AWS service
Service
apigateway.amazonaws.com
Action
lambda:InvokeFunction
Statement ID
allow-apigateway
→
Click Save. This gives API Gateway the green light to trigger your Lambda function.
