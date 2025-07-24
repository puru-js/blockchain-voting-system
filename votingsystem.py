from flask import Flask, request, render_template, jsonify
import hashlib
import json

app = Flask(__name__)

class BlockchainVoting:
    def __init__(self):
        self.chain = []
        self.votes = []
        self.voted_ids = set()
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'proof': proof,
            'previous_hash': previous_hash,
            'votes': self.votes
        }
        self.votes = []
        self.chain.append(block)
        return block

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def is_chain_valid(self, chain):
        previous = chain[0]
        for block in chain[1:]:
            if block['previous_hash'] != self.hash(previous):
                return False
            if hashlib.sha256(str(block['proof']**2 - previous['proof']**2).encode()).hexdigest()[:4] != '0000':
                return False
            previous = block
        return True

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                return new_proof
            new_proof += 1

    def add_vote(self, voter_id, candidate):
        if voter_id in self.voted_ids:
            return False  # Already voted

        self.votes.append({'voter_id': voter_id, 'candidate': candidate})
        self.voted_ids.add(voter_id)

        # Save vote to file
        try:
            with open('votes.json', 'r') as f:
                existing_votes = json.load(f)
        except FileNotFoundError:
            existing_votes = []

        existing_votes.append({'voter_id': voter_id, 'candidate': candidate})
        with open('votes.json', 'w') as f:
            json.dump(existing_votes, f, indent=4)

        return True

# Initialize blockchain
blockchain = BlockchainVoting()

@app.route('/')
def home():
    return render_template('vote.html')

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    voter_id = request.form['voter_id']
    candidate = request.form['candidate']

    success = blockchain.add_vote(voter_id, candidate)

    if success:
        return "<h2>Vote submitted successfully!</h2><a href='/'>Back</a>"
    else:
        return "<h2>You have already voted!</h2><a href='/'>Back</a>"

@app.route('/results')
def show_results():
    try:
        with open('votes.json', 'r') as f:
            votes = json.load(f)
    except FileNotFoundError:
        votes = []
    return jsonify(votes)

if __name__ == '__main__':
    app.run(debug=True)
