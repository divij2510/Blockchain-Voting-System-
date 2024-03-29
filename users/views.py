from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from web3 import Web3
from .models import Candidate, Vote, Voter
from .serializers import CandidateSerializer, VoteSerializer
import random
from django.conf import settings
from django.core.mail import send_mail

# Connect to the local Ganache blockchain
ganache_url = settings.BLOCKCHAIN_SERVER_URL
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Load the contract ABI and address

contract_abi = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "candidateId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "name",
                "type": "string"
            }
        ],
        "name": "CandidateAdded",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "voteId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "candidateId",
                "type": "uint256"
            }
        ],
        "name": "VoteCast",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "candidateCount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "candidates",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            },
            {
                "internalType": "string",
                "name": "name",
                "type": "string"
            },
            {
                "internalType": "uint256",
                "name": "voteCount",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [],
        "name": "voteCount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "votes",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "blockId",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "uniqueId",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "candidateId",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_name",
                "type": "string"
            }
        ],
        "name": "addCandidate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_candidateId",
                "type": "uint256"
            }
        ],
        "name": "vote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getVoteCount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_voteId",
                "type": "uint256"
            }
        ],
        "name": "getVote",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    }
]



contract_address = "0x826444067dFC409BD9a6c223f80B268Fa73F3DCb" # deployed contract address

# Create a contract instance
contract = w3.eth.contract(address=contract_address, abi=contract_abi)
accounts = w3.eth.accounts

class SendEmailView(APIView):
    def post(self, request):
        to_email = request.data.get('email')

        try:
            voter = Voter.objects.get(email_id=to_email)
        except Voter.DoesNotExist:
            return Response({'error':'Invalid Voter Email'},status=status.HTTP_400_BAD_REQUEST)

        otp = ''.join(random.choices('0123456789', k=6))
        request.session['otp']=otp
        request.session['email']=to_email

        subject = 'Access Election On Electify'
        message = f'Your secret code is :{otp}, Do not share it with anyone! This is an autogenerated email, do not reply to this!'
        from_email = settings.EMAIL_HOST_USER
        recipients = [to_email]
        send_mail(subject, message, from_email, recipients, fail_silently=True)
        return Response(status=status.HTTP_200_OK)

class VerifyEmailView(APIView):
    def post(self, request):
        otp = request.data.get('otp')

        try:
            voter = Voter.objects.get(email_id=request.session.get('email'))
        except Voter.DoesNotExist:
            return Response({'error':'Invalid Voter Session'},status=status.HTTP_400_BAD_REQUEST)

        if otp == request.session.get('otp'):
            voter.delete()
            return Response(status=status.HTTP_200_OK)

        return Response({'error':'Incorrect OTP!'},status=status.HTTP_400_BAD_REQUEST)

class AddCandidateView(APIView):
    def post(self, request):
        sender_account = accounts[0]
        candidate_name = request.data.get('name')
        tx_hash = contract.functions.addCandidate(candidate_name).transact({'from': sender_account})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        event_log = tx_receipt.logs[0]
        decoded_event = contract.events.CandidateAdded().process_log(event_log)
        candidate_id = decoded_event.args['candidateId']

        candidate = Candidate.objects.create(name=candidate_name, w3id=candidate_id)
        serializer = CandidateSerializer(candidate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class VoteCandidateView(APIView):
    def post(self, request):
        sender_account = accounts[1]
        candidate = Candidate.objects.get(name = request.data.get('name'))
        candidate_id = candidate.w3id
        tx_hash = contract.functions.vote(candidate_id).transact({'from': sender_account})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        event_log = tx_receipt.logs[0]
        decoded_event = contract.events.VoteCast().process_log(event_log)
        unique_id = decoded_event.args['voteId']
        vote_data = contract.functions.getVote(unique_id).call()
        block_id = vote_data[0]
        timestamp = vote_data[3]

        candidate = Candidate.objects.get(w3id=candidate_id)
        vote = Vote.objects.create(block_id=block_id, unique_id=tx_hash.hex(), candidate=candidate, timestamp=timestamp)
        serializer = VoteSerializer(vote)
        return Response(serializer.data)

class DisplayVotesView(APIView):
    def get(self, request):
        votes = Vote.objects.all()
        serializer = VoteSerializer(votes, many=True)
        return Response(serializer.data)

class AddVoterView(APIView):
    def post(self, request):
        emails = request.data.get('emails',[])
        if not emails:
            return Response({'error':'No emmails provided'}, status=status.HTTP_400_BAD_REQUEST)
        for email in emails:
            voter = Voter.objects.create(email_id=email)
        return Response({'message':'voters registered successfully'}, status=status.HTTP_201_CREATED)