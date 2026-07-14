
export const TASK_QUESTIONS = {
    how_fun: {
      q_fmt: "How fun is this game?",
      instruct_fmt: "how fun the game is to play",
    },
    advantage: {
      q_fmt: "Assuming both players play reasonably -- if the game does not end in a draw, how likely is it that the first player is going to win (not draw), and how likely is a draw?",
      instruct_fmt:
        "assuming both players play reasonably -- if the game does not end in a draw, how likely is it that the first player is going to win (not draw), and how likely is a draw",
    },
  };
  
export const SLIDERS = {
    how_fun: [{prompt: "How fun is this game?",
        label: "how_fun",
        labels: ["The least fun  of this class of grid-based game", "Neutral", "The most fun of this class of grid-based game"],}], 
    advantage: [
    { 
      prompt: "<p><strong>" + "If the game <i>does not end in a draw</i>, assuming both players play reasonably, how likely is it that the first player is going to win (<i>not draw</i>)?" + "</strong></p><p>    </p>",
      name: "firstplayer_response",
      labels: [
            "First player definitely going to <strong>lose</strong>",
            "Equally likely to <strong>win or lose</strong>",
            "First player definitely going to <strong>win</strong>",
          ],
    },
    {
      prompt: "<p><strong>" + "Assuming both players play reasonably, how likely is the game to end in a draw?" + "</strong></p><p>    </p>",
      name: "draw_response",
      labels: ["Impossible to end in a draw", "Equally likely to end in a draw or not",
        "Definitely going to end in a draw",],
    },
  
  ]
}