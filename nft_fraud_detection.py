import os
import json
import requests
import joblib
import cv2
import numpy as np
from web3 import Web3
from dotenv import load_dotenv
from skimage.metrics import structural_similarity as ssim
from sklearn.linear_model import LinearRegression
import pandas as pd

# Load environment variables
load_dotenv()

ALCHEMY = os.getenv("ALCHEMY_API_URL")
KEY = os.getenv("PRIVATE_KEY")
OPENSEA_API = os.getenv("OPENSEA_API_KEY")



# Web3 Connection

# Connect to the Ethereum network
w3 = Web3(Web3.HTTPProvider(ALCHEMY))

# Get block by number
block_number = 123456  # Replace with the desired block number or use 'latest'
block = w3.eth.get_block(block_number)

print(block)

# NFT Collection Data Fetching (Using OpenSea API)
url = os.getenv("url")
headers = {"X-API-KEY": OPENSEA_API}

response = requests.get(url, headers=headers)
data = response.json()
print(response.status_code)
print(response.json())


if "assets" not in data:
    print("Error:'assets'key missing in API response")
    print("Response",json.dumps(data,indent=4))
else:
    for asset in data["assets"]:
        print(asset)
nfts = []
for asset in data["assets"]:
    nfts.append({
        "name": asset["name"],
        "image": asset["image_url"],
        "price": asset.get("last_sale", {}).get("total_price", None),
        "owner": asset["owner"]["address"],
        "traits": asset["traits"]
    })

# Save data
with open("nft_data.json", "w") as f:
    json.dump(nfts, f, indent=4)

print("[✅] NFT Data Fetched and Saved.")




# AI Model for NFT Valuation

data = {
    "rarity_score": [45, 67, 89, 120, 150, 30, 110, 95],
    "num_sales": [3, 10, 25, 50, 5, 12, 45, 20],
    "artist_reputation": [7, 9, 6, 8, 10, 5, 9, 8],
    "price": [2.1, 5.4, 10.2, 20.1, 1.5, 3.2, 15.8, 9.0]
}
df = pd.DataFrame(data)

X = df.drop(columns=["price"])
y = df["price"]

model = LinearRegression()
model.fit(X, y)
joblib.dump(model, "nft_valuation_model.pkl")

print("[✅] AI Model for NFT Valuation Trained.")

# Image-Based NFT Fraud Detection

def load_image(image_path):
    return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def compare_images(img1, img2):
    score, _ = ssim(img1, img2, full=True)
    return score

image1 = load_image("nft1.png")
image2 = load_image("nft2.png")

similarity_score = compare_images(image1, image2)
if similarity_score > 0.9:
    print("[⚠️] Potential NFT Plagiarism Detected!")
else:
    print("[✅] NFT is unique.")


# Smart Contract Deployment (Hardhat)
solidity_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract NFTFraudDetection {
    struct Report {
        address reporter;
        string nftUrl;
        string reason;
    }

    Report[] public reports;

    event FraudReported(address indexed reporter, string nftUrl, string reason);

    function reportFraud(string memory _nftUrl, string memory _reason) public {
        reports.push(Report(msg.sender, _nftUrl, _reason));
        emit FraudReported(msg.sender, _nftUrl, _reason);
    }

    function getReports() public view returns (Report[] memory) {
        return reports;
    }
}
"""

with open("contracts/NFTFraudDetection.sol", "w") as f:
    f.write(solidity_code)

print("[✅] Smart Contract Created.")

# Deploy Smart Contract
contract_address = None

def deploy_contract():
    global contract_address

    os.system("npx hardhat compile")
    
    # Hardhat deployment script
    deploy_script = """
    const hre = require("hardhat");

    async function main() {
      const NFTFraudDetection = await hre.ethers.getContractFactory("NFTFraudDetection");
      const contract = await NFTFraudDetection.deploy();
      await contract.deployed();
      console.log(`Contract deployed to: ${contract.address}`);
    }

    main().catch((error) => {
      console.error(error);
      process.exitCode = 1;
    });
    """

    with open("scripts/deploy.js", "w") as f:
        f.write(deploy_script)

    os.system("npx hardhat run scripts/deploy.js --network goerli")
    print("[✅] Smart Contract Deployed.")

deploy_contract()

# Interact with the Contract
contract_abi = [
    "function reportFraud(string memory _nftUrl, string memory _reason) public",
    "function getReports() public view returns (tuple(address,string,string)[] memory)"
]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def report_nft_fraud(nft_url, reason):
    tx = contract.functions.reportFraud(nft_url, reason).build_transaction({
        'gas': 500000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'from': w3.eth.account.privateKeyToAccount(PRIVATE_KEY).address,
        'nonce': w3.eth.get_transaction_count(w3.eth.account.privateKeyToAccount(PRIVATE_KEY).address),
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print("[✅] Fraud Reported. Tx Hash:", tx_hash.hex())

# Example: Reporting Fake NFT
report_nft_fraud("https://example.com/fake_nft.png", "Fake NFT Detected")

print("[✅] NFT Fraud Detection & Valuation System Complete.")