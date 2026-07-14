import React from "react";
import {
  usePlayer,
  usePlayers,
  useRound,
  useStageTimer,
} from "@empirica/core/player/classic/react";
import { Button } from "../components/Button";

import { useState, useEffect } from "react";
import {DRAW_OUTCOME_TXT, WIN_OUTCOME_TXT, LOSS_OUTCOME_TXT} from "../Constants.jsx";

export function Play() {

  const [showDrawRequest, setShowDrawRequest] = useState(false);

  const player = usePlayer();
  const players = usePlayers();
  const round = useRound();
  const timer = useStageTimer();
  const partner = players.filter((p) => p.id !== player.id)[0];
  const playerOrder = player.round.get("playerOrder");

  const requestedDraw = round.get("requestedDraw")
  const drawWasRejected = round.get("rejectedDraw")

  // var myTurn = 2
  // console.log("timer: ", timer.elapsed)
  // var currentTime = timer.elapsed

  const stimID = round.get("stimuliID");
  const gameMetaData = round.get("stimuliMetaData");
  var numRows = round.get("numRows");
  var numCols = round.get("numCols");
  const winConds = round.get("winConds");

  // extra saving for later 
  player.round.set("stimuliID", stimID)

  var CELL_SIZE = 80; 
  if (numRows >= 9 && numCols >= 9){
    CELL_SIZE = 40
  } 
  else if (numRows >= 7 && numCols >= 7){
    CELL_SIZE = 60
  } 
const buttonStyle = {
  width: CELL_SIZE,
  height: CELL_SIZE,
  itemsAlign: "center", // Note: This should be 'alignItems' in a real CSS-in-JS solution
  backgroundColor: "white",
  color: "white",
  fontWeight: "bold",
  border: "1px solid black",
  verticalAlign: "top",
  fontSize: "24px",
  display: "inline-block",
};

const visitStylePlayer1 = {
  width: CELL_SIZE,
  height: CELL_SIZE,
  itemsAlign: "center", // Note: This should be 'alignItems' in a real CSS-in-JS solution
  backgroundColor: "blue",
  color: "blue",
  fontWeight: "bold",
  border: "1px solid black",
  verticalAlign: "top",
  fontSize: "24px",
  display: "inline-block",
};

const visitStylePlayer2 = {
  width: CELL_SIZE,
  height: CELL_SIZE,
  itemsAlign: "center", // Note: This should be 'alignItems' in a real CSS-in-JS solution
  backgroundColor: "red",
  color: "red",
  fontWeight: "bold",
  border: "1px solid black",
  verticalAlign: "top",
  fontSize: "24px",
  display: "inline-block",
};
  // var requestedDraw = false
  // var playerRequestedDraw = 0

  const drawRequest = () => {
    setShowDrawRequest(true);

    //have a timeout on the draw request?
    // setTimeout(() => {
    //   setShowDrawRequest(false);
    //   round.set("requestedDraw", "None") 
    // }, 4000);

  };


  // console.log("stimuli ID: ", stimID, numRows, numCols, winConds);

  var board = round.get("board");
  //resetTimer();

  function parseGameDynamics(gameMetaData) {
    var specialConds = {
      player1: "default",
      player2: "default",
      K: "wins",
      player1K: 3,
      player2K: 3,
    }; // default
    var specialTurnConds = { player1: 1, player2: 1 }; // default

    var gameDescription = gameMetaData["stimuli_id"];

    // k-in-a-row wins or loses
    if (gameDescription.includes("loses")) {
      specialConds["K"] = "loses";
    }

    // can player 1/2 play twice in a row?
    if (
      gameDescription.includes(
        "second player can place 2 pieces as their first move"
      )
    ) {
      specialTurnConds["player2"] = 2;
    }
    if (
      gameDescription.includes(
        "first player can place 2 pieces as their first move"
      )
    ) {
      specialTurnConds["player1"] = 2;
    }

    if (gameMetaData["diff-win"] == 0) {
      // same number needed to win for both players
      specialConds["player1K"] = gameMetaData["N"];
      specialConds["player2K"] = gameMetaData["N"];
    } else if (gameMetaData["diff-win"] == 1) {
      // player 2 needs one LESS to win
      specialConds["player1K"] = gameMetaData["N"] //+ 1;
      specialConds["player2K"] = gameMetaData["N"] - 1;
    }

    if (gameMetaData["label"] == "no-diag") {
      specialConds["player1"] = "noDiag";
      specialConds["player2"] = "noDiag";
    }

    // ADDED -- correct for diag
    if (gameMetaData["label"] == "only-diag") {
      specialConds["player1"] = "onlyDiag";
      specialConds["player2"] = "onlyDiag";
    }

    if (gameMetaData["label"].includes("player1-constraint")) {
      // constraint on the first player
      var diagWin = gameMetaData["player1-diag-win"];
      var horizWin = gameMetaData["player1-hv-win"];
      if (diagWin == 0 && horizWin == 1) {
        specialConds["player1"] = "noDiag";
      } else if (diagWin == 1 && horizWin == 0) {
        specialConds["player1"] = "onlyDiag";
      }
    }

    if (gameMetaData["label"].includes("player2-constraint")) {
      // constraint on the first player
      var diagWin = gameMetaData["player2-diag-win"];
      var horizWin = gameMetaData["player2-hv-win"];
      if (diagWin == 0 && horizWin == 1) {
        specialConds["player2"] = "noDiag";
      } else if (diagWin == 1 && horizWin == 0) {
        specialConds["player2"] = "onlyDiag";
      }
    }

    return { winConds: specialConds, openingMove: specialTurnConds };
  }

  //var specialConds = {"player1": "default", "player2": "default", "K": "wins"};
  //var specialConds = {"player1": "square", "player2": "square", "K": "wins"};
  // For some games, either player 1 or player 2 can play 2 moves at once
  var parsedGame = parseGameDynamics(gameMetaData);
  var specialConds = parsedGame["winConds"];
  var specialTurnConds = parsedGame["openingMove"];

  function isGameOver(board, M, N, specialConds = {}) {
    /* Check if the game is over
        Returns a list -- [gameStatus, winner]
        gameStatus: if True, the game is over; if False, the game is still going
        winner: the player ID that won, if "null" then ended in a draw
    
        specialConds specifies any special win conditions on either player
            If "default", horiz, vertical, and diagonal all count
        And/Or whether K in a row actually loses instead of (by default) wins
    */

    // Check if there are any empty cells left as we look for win conds
    // If no empty cells left at end, it's a draw
    let isEmptyCellFound = false;
    for (let x = 0; x < M; x++) {
      for (let y = 0; y < N; y++) {
        // Track empty cell presence for draw checking
        if (board[x][y] === 0) {
          isEmptyCellFound = true;
          continue;
        }

        // Check if a line of K same symbols starts from (x, y)
        // Help from GPT
        function checkLine(x, y, dx, dy, player, specialConds) {
          var K = specialConds["player" + String(player) + "K"];
          for (let i = 0; i < K; i++) {
            // Check if the position is outside the board
            if (
              x + i * dx >= M ||
              x + i * dx < 0 ||
              y + i * dy >= N ||
              y + i * dy < 0
            ) {
              return false;
            }
            // Check if the cell belongs to the player
            if (board[x + i * dx][y + i * dy] !== player) {
              return false;
            }
          }
          return true; // All cells in line belong to the player
        }

        function checkSquare(x, y, player, specialConds) {
          var K = specialConds["player" + String(player) + "K"];
          for (let i = 0; i < K; i++) {
            for (let j = 0; j < K; j++) {
              if (x + i >= M || y + j >= N || board[x + i][y + j] !== player) {
                return false;
              }
            }
          }
          return true;
        }

        var currentPlayerID = board[x][y];
        var currentPlayerStr = "player" + String(currentPlayerID);
        // get K-in-a-row condition for that player
        // Include particular direction checks here
        // These checks are done for the player ID at that position
        var horizontalCheck = checkLine(
          x,
          y,
          1,
          0,
          currentPlayerID,
          specialConds
        );
        var verticalCheck = checkLine(
          x,
          y,
          0,
          1,
          currentPlayerID,
          specialConds
        );
        var diagonalDownRightCheck = checkLine(
          x,
          y,
          1,
          1,
          currentPlayerID,
          specialConds
        );
        var diagonalDownLeftCheck = checkLine(
          x,
          y,
          1,
          -1,
          currentPlayerID,
          specialConds
        );
        var squareCheck = checkSquare(x, y, currentPlayerID, specialConds);

        // Get special conditions for that player
        var playerSpecialConds = specialConds[currentPlayerStr];

        // We only care if (at least) one direction is met
        // Depending on win conditions, check "any" on those directions
        if (playerSpecialConds == "noDiag") {
          var checkDirections = [horizontalCheck, verticalCheck];
        } else if (playerSpecialConds == "onlyDiag") {
          var checkDirections = [diagonalDownRightCheck, diagonalDownLeftCheck];
        } else if (playerSpecialConds == "square") {
          var checkDirections = [squareCheck];
        } else {
          // default
          var checkDirections = [
            horizontalCheck,
            verticalCheck,
            diagonalDownRightCheck,
            diagonalDownLeftCheck,
          ];
        }

        // Check if any condition is met
        if (checkDirections.some((condMet) => condMet === true)) {
          // console.log("Game over!!!!", board[x][y]);
          // The ID of the player at the cell we started looking
          var playerMetCond = board[x][y];
          // Note: if "K in a row wins" this player won
          // Else, if "K in a row loses", this player lost [other player won]
          if (specialConds["K"] === "wins") {
            var playerWon = playerMetCond;
          } else {
            var playerWon = playerMetCond === 1 ? 2 : 1;
          }
          return [true, playerWon];
        }
      }
    }

    // If no winner and no empty cell found, it's a draw
    if (!isEmptyCellFound) {
      return [true, 0];
    }

    // If no winner but empty cells exist, game is still going
    return [false, null];
  }

  function clearBoard(board) {
    for (let i = 0; i < board.length; i++) {
      for (let j = 0; j < board[i].length; j++) {
        board[i][j] = 0;
      }
    }
    round.set("board", board);
    player.round.set("gameOutcome", "TBD");
    partner.round.set("gameOutcome", "TBD");
    console.log("cleared board: ", board)
  }

  function requestDraw(){
    round.set("requestedDraw", playerOrder)
    var allDrawsSoFar = round.get("allDrawRequests")
    var currentTime = timer.elapsed
    console.log("draw request time!!!! ", currentTime)
    allDrawsSoFar.push([playerOrder, currentTime])
    round.set("allDrawRequests", allDrawsSoFar)
    drawRequest()
  }

  function surrender(){
    //round.set("surrendered", playerOrder)
    var currentTime = timer.elapsed
    console.log("surrender time!!!! ", currentTime)
    round.set("surrenderMade", [playerOrder, currentTime])
    
    console.log("request player: ", playerOrder)
  
    // you immediately lose
    var gameWinner = playerOrder === 1 ? 2 : 1; 
    console.log("winning player: ", gameWinner)
  
    round.set("gameOver", true);
    round.set("gameWinner", gameWinner);
    var partnerOutcome =  WIN_OUTCOME_TXT;
    var yourOutcome = LOSS_OUTCOME_TXT;

    player.round.set("gameOutcome", yourOutcome);
    partner.round.set("gameOutcome", partnerOutcome);

     //round.set("requestedDraw", "None")
  }



  function cellEmpty(board, i, j) {
    if (board[i][j] === 1 || board[i][j] === 2) {
      return false;
    } else {
      return true;
    }
  }

  function getEmptyCells(board) {
    let emptyCells = [];

    for (let i = 0; i < board.length; i++) {
      for (let j = 0; j < board[i].length; j++) {
        if (cellEmpty(board, i, j)) {
          emptyCells.push([i, j]);
        }
      }
    }

    return emptyCells;
  }

  function getRandomEmptyCell(board) {
    const emptyCells = getEmptyCells(board);
    if (emptyCells.length === 0) {
      return null; // No empty cells available
    }
    const randomIndex = Math.floor(Math.random() * emptyCells.length);

    console.log("random cell: ", emptyCells[randomIndex])
    return emptyCells[randomIndex];
  }

  function acceptDraw(){
    round.set("gameOver", true);
    round.set("gameWinner", 0);

    var yourOutcome = DRAW_OUTCOME_TXT;
    var partnerOutcome = DRAW_OUTCOME_TXT;

    player.round.set("gameOutcome", yourOutcome);
    partner.round.set("gameOutcome", partnerOutcome);

    var allDrawAccepts = round.get("allDrawAccepts")
    var currentTime = timer.elapsed
    allDrawAccepts.push(currentTime)

    console.log("draw accept time!!!! ", currentTime)

    round.set("allDrawAccepts", allDrawAccepts)

    round.set("requestedDraw", "None")
  }

  function rejectDraw(){ 
    round.set("rejectedDraw", requestedDraw)
    round.set("requestedDraw", "None")

    var allDrawRejects = round.get("allDrawRejects")
    var currentTime = timer.elapsed
    allDrawRejects.push(currentTime)

    console.log("draw reject time!!!! ", currentTime)


    round.set("allDrawRejects", allDrawRejects)

    setTimeout(() => {
      setShowDrawRequest(false);
      round.set("rejectedDraw", "None") 
    }, 4000);
    
  }




  function countMovesSoFar(board) {
    var num_moves = 0;
    for (let i = 0; i < board.length; i++) {
      for (let j = 0; j < board[i].length; j++) {
        if (board[i][j] != 0) {
          num_moves += 1;
        }
      }
    }
    return num_moves;
  }

  const count = countMovesSoFar(board);
  const gameOutcome = player.round.get("gameOutcome");

  // setTimeout(() => {
  //   /* Code to run after 4 seconds */
  // }, 10000)

  if (playerOrder === 1) {
    var parsedPlayerOrder = "first";
    if (
      specialTurnConds["player1"] === 1 &&
      specialTurnConds["player2"] === 1
    ) {
      var myTurn = count % 2 === 0;
    } else if (
      specialTurnConds["player1"] === 2 &&
      specialTurnConds["player2"] === 1
    ) {
      // player 1 plays twice in a row
      // they can play if the count is 0 or 1, or then if count % 2 === 1 [since modulo switched]
      if (count < 2) {
        var myTurn = true;
      } else {
        var myTurn = count % 2 === 1;
      }
    } else if (
      specialTurnConds["player1"] === 1 &&
      specialTurnConds["player2"] === 2
    ) {
      // player 2 plays twice in a row
      // they can play if the count is 0, or then if count % 2 === 1 [since modulo switched]
      if (count < 1) {
        var myTurn = true;
      } else {
        var myTurn = count % 2 === 1 && count != 1;
      }
    }
  } else {
    var parsedPlayerOrder = "second";
    var myTurn = count % 2 === 1 && count != 0;

    if (
      specialTurnConds["player1"] === 1 &&
      specialTurnConds["player2"] === 1
    ) {
      var myTurn = count % 2 === 1 && count != 0;
    } else if (
      specialTurnConds["player1"] === 2 &&
      specialTurnConds["player2"] === 1
    ) {
      // player 1 plays twice in a row
      // then if count % 2 === 0 [since modulo switched]
      var myTurn = count % 2 === 0 && count != 0;
    } else if (
      specialTurnConds["player1"] === 1 &&
      specialTurnConds["player2"] === 2
    ) {
      // player 2 plays twice in a row
      // they can play the second and third moves [zero-indexed]
      // then if count % 2 === 0 [since modulo switched]
      if (count != 0 && (count === 1 || count === 2)) {
        var myTurn = true;
      } else {
        var myTurn = count % 2 === 0 && count != 0;
      }
    }
  }


  var attemptMove = (i, j) => {

    var gameStatus = isGameOver(board, numRows, numCols, specialConds);

    // console.log("game status: ", gameStatus);
    var gameOver = gameStatus[0];
    var gameWinner = gameStatus[1];

    if (gameOver || !cellEmpty(board, i, j) || !myTurn) {
      return;
    }

    // note: color here is based on player order rather than player ID
    // this means that you might be red one round and blue the next.
    board[i][j] = playerOrder;
    round.set("board", [...board]);


    var allBoardsSoFar = round.get("allBoards")
    allBoardsSoFar.push(board)
    round.set("allBoards", allBoardsSoFar)
    var moveTimes = round.get("moveTimes")
    var currentTime = timer.elapsed
    moveTimes.push(currentTime)
    round.set("moveTimes", moveTimes)

    var gameStatus = isGameOver(board, numRows, numCols, specialConds);
    var gameOver = gameStatus[0];
    var gameWinner = gameStatus[1];

    if (gameOver) {
      round.set("gameOver", true);
      round.set("gameWinner", gameWinner);

      if (gameWinner === 0) {
        var yourOutcome = DRAW_OUTCOME_TXT;
        var partnerOutcome = DRAW_OUTCOME_TXT;
      } else if (gameWinner === playerOrder) {
        var yourOutcome = WIN_OUTCOME_TXT;
        var partnerOutcome =  LOSS_OUTCOME_TXT;
      } else {
        var partnerOutcome =  WIN_OUTCOME_TXT;
        var yourOutcome = LOSS_OUTCOME_TXT;
      }

      player.round.set("gameOutcome", yourOutcome);
      partner.round.set("gameOutcome", partnerOutcome);

      return true;
    }
    return false;
  };

  // Add the state for hovered cell
const [hoveredCell, setHoveredCell] = useState({ row: null, col: null });

// Define hover styles
const hoverStylePlayer1 = {
  ...buttonStyle,
  backgroundColor: "rgba(0, 0, 255, 0.2)", // Light blue
};

const hoverStylePlayer2 = {
  ...buttonStyle,
  backgroundColor: "rgba(255, 0, 0, 0.2)", // Light red
};

// Handle mouse enter
const handleMouseEnter = (rowIndex, colIndex) => {
  if (myTurn && board[rowIndex][colIndex] === 0) {
    setHoveredCell({ row: rowIndex, col: colIndex });
  }
};

// Handle mouse leave
const handleMouseLeave = () => {
  setHoveredCell({ row: null, col: null });
};

  return (
    <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <p style={{ textAlign: "center" }}>
        <strong>In this game,</strong> you will play on a{" "}
        
        <strong>
          {numRows} x {numCols} board
        </strong>
        .
      </p>
      <p style={{ textAlign: "center", marginBottom: "20px" }}>
      <br></br>
        <strong>The rules for this game are:</strong><br></br> {winConds}
      </p>
      <p style={{ textAlign: "center", marginBottom: "20px"  }}>
        You make the <strong>{parsedPlayerOrder}</strong> move.
      </p>

      {gameOutcome !== "TBD" && (
        <p style={{ textAlign: "center", color: 'purple', fontSize: '80', }}>
          <br></br>Game over! <strong>{gameOutcome}</strong><br></br>
          Please press <strong>Next</strong> to continue to the post-game question(s).
        </p>
      )}

      <br></br>
      <br></br>

      {myTurn && !round.get("gameOver") && <div>
        {<div className="popup" style={{ fontSize: '80', color: 'blue', fontWeight: 'bold', textAlign: 'center' }}>It's your turn!</div>}
        </div>}
      {!myTurn && !round.get("gameOver") && <div>
          {<div className="popup" style={{ fontSize: '80', color: 'red', fontWeight: 'bold', textAlign: 'center' }}>Wait for the other player to make a move...</div>}
      
          </div>}


      {round.get("requestedDraw") != "None" && requestedDraw != playerOrder && <div>
        {<div className="popup" style={{ fontSize: '80', color: 'red', fontWeight: 'bold', textAlign: 'center' }}>Your opponent requested a draw -- do you accept?</div>}
        
        <div style={{ textAlign: "center" }}>
        {<div style={{ display: "inline-block", margin: "0 10px" }}>
          <Button handleClick={() => acceptDraw()}>
            Yes
          </Button>
        </div>}

        {<div style={{ display: "inline-block", margin: "0 10px" }}>
          <Button handleClick={() => rejectDraw()}>
            No
          </Button>
        </div>}

        </div>
      
      
      </div>}

      {round.get("rejectedDraw") != "None" && drawWasRejected == playerOrder && <div>
        {<div className="popup" style={{ fontSize: '80', color: 'red', fontWeight: 'bold', textAlign: 'center' }}>Your request to end in a draw has been denied. Keep playing!</div>}      
      
      </div>}



      <br></br>
      <br></br>
{/* 
      <div style={{ textAlign: "center", position: "relative",  justifyContent: 'center',  marginBottom: "20px", marginTop: "20px" }}>
  <div style={{ position: "relative", textAlign: "center", alignItems: "center" }}>
    {board.map((arr, rowIndex) => (
      <div key={rowIndex} style={{ display: "flex", alignItems: "center" }}>
        {arr.map((cell, colIndex) => (
          <div
            key={`${rowIndex}-${colIndex}`}
            onClick={() => attemptMove(rowIndex, colIndex)} 
            style={
              board[rowIndex][colIndex] === 0
                ? buttonStyle
                : board[rowIndex][colIndex] === 1
                  ? visitStylePlayer1
                  : visitStylePlayer2
            }
          ></div>

        ))}
      </div>
    ))} */}
    
    <div style={{ textAlign: "center", position: "relative",  justifyContent: 'center',  marginBottom: "20px", marginTop: "20px" }}>
    <div style={{ position: "relative", textAlign: "center", alignItems: "center" }}>
    {board.map((arr, rowIndex) => (
      <div key={rowIndex} style={{ display: "flex", alignItems: "center" }}>
        {arr.map((cell, colIndex) => (
          <div
            key={`${rowIndex}-${colIndex}`}
            onClick={() => attemptMove(rowIndex, colIndex)}
            onMouseEnter={() => handleMouseEnter(rowIndex, colIndex)}
            onMouseLeave={() => handleMouseLeave()}
            style={
              hoveredCell.row === rowIndex && hoveredCell.col === colIndex
                ? playerOrder === 1
                  ? hoverStylePlayer1
                  : hoverStylePlayer2
                : board[rowIndex][colIndex] === 0
                ? buttonStyle
                : board[rowIndex][colIndex] === 1
                ? visitStylePlayer1
                : visitStylePlayer2
            }
          ></div>
        ))}
      </div>
    ))}
    
    {/* Conditional overlay for the board */}
    {(!myTurn && !round.get("gameOver")) && (
      <div style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(128, 128, 128, 0.8)", // Gray with opacity
        pointerEvents: "none" // Allow clicks to pass through
      }}></div>
    )}
  </div>
</div>


      <br></br>
      <br></br>


      <div style={{ textAlign: "center", marginTop: "20px" }}>

        
        {/* <div style={{ display: "inline-block", margin: "0 10px" }}>
          <Button handleClick={() => clearBoard(board)}>Restart</Button>
        </div>*/}

  {!round.get("gameOver") && 
        <div style={{ display: "inline-block", margin: "0 10px" }}>
          {<Button handleClick={() => surrender()}>
            Surrender
          </Button>}
        </div>
        }  

        {!round.get("gameOver") && 
        <div style={{ display: "inline-block", margin: "0 10px" }}>
          {<Button handleClick={() => requestDraw()}>
            Request a Draw
          </Button>}
        </div>
        }  



        <div></div>

        {round.get("gameOver") && <div>
        {<Button handleClick={() => player.stage.set("submit", true)}>
        Next
          </Button>}
        </div>}


      </div>
    </div>
  );
}
