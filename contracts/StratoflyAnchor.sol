// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract StratoflyAnchor {
    struct Anchor {
        string memoryHash;
        uint256 timestamp;
        address anchoredBy;
    }

    mapping(string => Anchor) public anchors;
    mapping(string => uint256) public anchorCount;

    event MemoryAnchored(string indexed agentId, string memoryHash, uint256 timestamp, address indexed anchoredBy);

    function anchor(string calldata agentId, string calldata memoryHash) external returns (uint256) {
        require(bytes(agentId).length > 0, "empty agentId");
        require(bytes(memoryHash).length == 66, "hash must be 0x + 64 hex chars");
        anchors[agentId] = Anchor(memoryHash, block.timestamp, msg.sender);
        anchorCount[agentId] += 1;
        emit MemoryAnchored(agentId, memoryHash, block.timestamp, msg.sender);
        return block.timestamp;
    }

    function getAnchor(string calldata agentId) external view returns (string memory, uint256, address) {
        Anchor storage a = anchors[agentId];
        return (a.memoryHash, a.timestamp, a.anchoredBy);
    }

    function getAnchorCount(string calldata agentId) external view returns (uint256) {
        return anchorCount[agentId];
    }
}