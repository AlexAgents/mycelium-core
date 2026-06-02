// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract VotingCore {

    // ─────────────────────────────────────────────────────────────
    // Errors
    // ─────────────────────────────────────────────────────────────

    error Unauthorized();
    error InvalidStage();
    error CandidateAlreadyExists();
    error CandidateNotFound();
    error AlreadyVoted();
    error NotWhitelisted();
    error InvalidCandidateCount();
    error VotingNotStarted();
    error VotingAlreadyFinished();

    // ─────────────────────────────────────────────────────────────
    // Types
    // ─────────────────────────────────────────────────────────────

    enum Stage {
        Setup,
        Active,
        Finished
    }

    struct Candidate {
        string name;
        string party;
        bool registered;
        uint256 votes;
    }

    // ─────────────────────────────────────────────────────────────
    // State
    // ─────────────────────────────────────────────────────────────

    address public owner;

    Stage public stage;

    mapping(address => Candidate) private candidates;

    address[] private candidateList;

    mapping(address => bool) public whitelist;

    address[] private voterList;

    mapping(address => bool) public hasVoted;

    // ─────────────────────────────────────────────────────────────
    // Events
    // ─────────────────────────────────────────────────────────────

    event CandidateAdded(
        address indexed candidate,
        string name,
        string party
    );

    event VoterWhitelisted(address indexed voter);

    event StageChanged(uint8 newStage);

    event VoteCast(
        address indexed voter,
        address indexed candidate
    );

    // ─────────────────────────────────────────────────────────────
    // Modifiers
    // ─────────────────────────────────────────────────────────────

    modifier onlyOwner() {
        if (msg.sender != owner) {
            revert Unauthorized();
        }
        _;
    }

    modifier onlyStage(Stage requiredStage) {
        if (stage != requiredStage) {
            revert InvalidStage();
        }
        _;
    }

    // ─────────────────────────────────────────────────────────────
    // Constructor
    // ─────────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
        stage = Stage.Setup;
    }

    // ─────────────────────────────────────────────────────────────
    // Candidate management
    // ─────────────────────────────────────────────────────────────

    function addCandidate(
        string calldata name,
        string calldata party,
        address addr
    )
        external
        onlyOwner
        onlyStage(Stage.Setup)
    {
        if (candidates[addr].registered) {
            revert CandidateAlreadyExists();
        }

        uint256 nextCount = candidateList.length + 1;

        if (nextCount > 10) {
            revert InvalidCandidateCount();
        }

        candidates[addr] = Candidate({
            name: name,
            party: party,
            registered: true,
            votes: 0
        });

        candidateList.push(addr);

        emit CandidateAdded(addr, name, party);
    }

    // ─────────────────────────────────────────────────────────────
    // Whitelist
    // ─────────────────────────────────────────────────────────────

    function addVotersBatch(
        address[] calldata voters
    )
        external
        onlyOwner
        onlyStage(Stage.Setup)
    {
        for (uint256 i = 0; i < voters.length; i++) {

            address voter = voters[i];

            if (!whitelist[voter]) {
                whitelist[voter] = true;
                voterList.push(voter);

                emit VoterWhitelisted(voter);
            }
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Stage control
    // ─────────────────────────────────────────────────────────────

    function startVoting()
        external
        onlyOwner
        onlyStage(Stage.Setup)
    {
        if (candidateList.length < 2) {
            revert InvalidCandidateCount();
        }

        stage = Stage.Active;

        emit StageChanged(uint8(stage));
    }

    function finishVoting()
        external
        onlyOwner
        onlyStage(Stage.Active)
    {
        stage = Stage.Finished;

        emit StageChanged(uint8(stage));
    }

    // ─────────────────────────────────────────────────────────────
    // Voting
    // ─────────────────────────────────────────────────────────────

    function castVote(
        address candidate
    )
        external
        onlyStage(Stage.Active)
    {
        if (!whitelist[msg.sender]) {
            revert NotWhitelisted();
        }

        if (hasVoted[msg.sender]) {
            revert AlreadyVoted();
        }

        if (!candidates[candidate].registered) {
            revert CandidateNotFound();
        }

        hasVoted[msg.sender] = true;

        candidates[candidate].votes += 1;

        emit VoteCast(msg.sender, candidate);
    }

    // ─────────────────────────────────────────────────────────────
    // Read API
    // ─────────────────────────────────────────────────────────────

    function isCandidate(
        address addr
    )
        external
        view
        returns (bool)
    {
        return candidates[addr].registered;
    }

    function getCandidate(
        address addr
    )
        external
        view
        returns (
            string memory name,
            string memory party,
            bool registered,
            uint256 votes
        )
    {
        Candidate memory c = candidates[addr];

        return (
            c.name,
            c.party,
            c.registered,
            c.votes
        );
    }

    function getCandidateAddresses()
        external
        view
        returns (address[] memory)
    {
        return candidateList;
    }

    function getVoterAddresses()
        external
        view
        returns (address[] memory)
    {
        return voterList;
    }

    function currentStage()
        external
        view
        returns (uint8)
    {
        return uint8(stage);
    }

    function totalCandidates()
        external
        view
        returns (uint256)
    {
        return candidateList.length;
    }

    function totalVoters()
        external
        view
        returns (uint256)
    {
        return voterList.length;
    }
}