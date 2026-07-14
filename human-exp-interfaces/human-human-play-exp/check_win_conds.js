

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


var board = [[1, 1, 2, 0, 0, 0, 0, 0, 0, 0],
[2, 1, 1, 1, 0, 0, 0, 0, 0, 0],
[0, 2, 1, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 1, 2, 0, 0, 0, 0, 0, 0],
[0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
[0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]];

var specialConds = {
      player1: "default",
      player2: "default",
      K: "wins",
      player1K: 4,
      player2K: 4,
    };
console.log('game over?', isGameOver(board, 10, 10,  specialConds))