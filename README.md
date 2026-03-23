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

Step 5 — DStep 2 — Create an S3 Bucket

Go to console.aws.amazon.com → search "S3" → click it
Click "Create bucket"
Bucket name: type something like quiz-website-yourname-2024 (must be globally unique — no spaces)
Region: leave as default (us-east-1)
Block Public Access settings: find the checkbox that says "Block all public access" → uncheck it → tick the confirmation box that appears
Scroll down → click "Create bucket"


Step 3 — Upload your HTML to S3

Click on your new bucket name to open it
Click the orange "Upload" button
Click "Add files" → select your index.html
Scroll down → click the orange "Upload" button
Wait for the green success message → click "Close"


Step 4 — Enable Static Website Hosting

Still inside your bucket → click the "Properties" tab (top navigation)
Scroll all the way down to "Static website hosting"
Click "Edit"
Select "Enable"
Index document: type index.html
Click "Save changes"
Scroll back down to Static website hosting — copy the "Bucket website endpoint" URL (looks like http://quiz-website-yourname.s3-website-us-east-1.amazonaws.com)


Step 5 — Add a Bucket Policy (make it public)

Click the "Permissions" tab
Scroll to "Bucket policy" → click "Edit"
Delete everything in the text box, then paste this exactly (replace YOUR-BUCKET-NAME with your actual bucket name):

json{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}

Click "Save changes"

Your site is now live at the S3 endpoint URL from Step 4!

Step 6 — Add CloudFront for HTTPS (recommended)

Search "CloudFront" in AWS → click "Create distribution"
Origin domain: click the dropdown → select your S3 bucket
Viewer protocol policy: select "Redirect HTTP to HTTPS"
Default root object: type index.html
Click "Create distribution"
Wait 5–15 minutes → your site is live at https://XXXXXXXX.cloudfront.net

That's your final URL — share it with anyone!
Once CloudFront is live, open your https://XXXX.cloudfront.net URL → enter your stats → hit Calculate → your Lambda runs the math and sends back the full results. Done!

===================================================================dhyaan de=====================================================================================
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
Click Save — API Gateway will auto-redeploy in about 30 seconds..


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


Fix the Default Root Object — 4 clicks
1.
You are already on the right page. Click the Edit button in the top-right of the Settings section (you can see it in your screenshot).
2.
Scroll down until you see a field called "Default root object". It is currently empty.
3.
Type exactly this into that field:
index.html
4.
Scroll to the bottom → click the orange "Save changes" button. CloudFront will re-deploy (another 1–2 min)


