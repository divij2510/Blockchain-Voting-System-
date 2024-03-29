// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voting {
    struct Vote {
        uint256 blockId;
        uint256 uniqueId;
        uint256 candidateId;
        uint256 timestamp;
    }

    struct Candidate {
        uint256 id;
        string name;
        uint256 voteCount;
    }

    mapping(uint256 => Vote) public votes;
    mapping(uint256 => Candidate) public candidates;
    uint256 public voteCount;
    uint256 public candidateCount;

    event CandidateAdded(uint256 indexed candidateId, string name);
    event VoteCast(uint256 indexed voteId, uint256 candidateId);

    function addCandidate(string memory _name) public {
        candidateCount++;
        candidates[candidateCount] = Candidate(candidateCount, _name, 0);
        emit CandidateAdded(candidateCount, _name);
    }

    function vote(uint256 _candidateId) public {
        require(_candidateId > 0 && _candidateId <= candidateCount, "Invalid candidate id");

        voteCount++;
        votes[voteCount] = Vote(
            block.number,
            voteCount,
            _candidateId,
            block.timestamp
        );
        candidates[_candidateId].voteCount++;
        emit VoteCast(voteCount, _candidateId);
    }

    function getVoteCount() public view returns (uint256) {
        return voteCount;
    }

    function getVote(uint256 _voteId) public view returns (uint256, uint256, uint256, uint256) {
        require(_voteId > 0 && _voteId <= voteCount, "Invalid vote id");
        Vote memory vote = votes[_voteId];
        return (vote.blockId, vote.uniqueId, vote.candidateId, vote.timestamp);
    }
}