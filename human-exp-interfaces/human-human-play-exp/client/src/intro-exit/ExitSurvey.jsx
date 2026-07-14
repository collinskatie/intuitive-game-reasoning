import { usePlayer } from "@empirica/core/player/classic/react";
import React, { useState } from "react";
import { Alert } from "../components/Alert";
import { Button } from "../components/Button";

export function ExitSurvey({ next }) {
  const labelClassName = "block text-sm font-medium text-gray-700 my-2";
  const inputClassName =
    "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-empirica-500 focus:border-empirica-500 sm:text-sm";
  const player = usePlayer();

  const [funOpponent, setFunOpp] = useState("");
  const [skill, setSkill] = useState("");
  const [fun, setFun] = useState("");
  const [notFun, setNotFun] = useState("");
  const [strategy, setStrategy] = useState("");
  const [feedback, setFeedback] = useState("");
  const [depth, setDepth] = useState("");
  

  function handleSubmit(event) {
    event.preventDefault();
    player.set("exitSurvey", {
      funOpponent, skill, fun, notFun, depth, feedback, strategy
    });
    console.log("set exit survey: ", player.get("exitSurvey"))
    next();
  }

  function handleEducationChange(e) {
    setEducation(e.target.value);
  }

  var CODE = "CH1OQ9N6"

  return (
    <div className="py-8 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <Alert title="Bonus">
        <p>
          Please submit the following code to Prolific to receive your payment:{" "}
          <strong>{CODE}</strong>.
        </p>
        {/* <p className="pt-1">
          Your final <strong>bonus</strong> is in addition of the{" "}
          <strong>1 base reward</strong> for completing the HIT.
        </p> */}
      </Alert>

      <form
        className="mt-12 space-y-8 divide-y divide-gray-200"
        onSubmit={handleSubmit}
      >
        <div className="space-y-8 divide-y divide-gray-200">
          <div>
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Exit Survey
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Thank your for participating in our study! We have a few final questions before the experiment ends.
              </p>
              <p>
                When done with the survey, please submit the following code to Prolific to receive your payment:{" "}
                <strong>{CODE}</strong>.
              </p>
            </div>

            <div className="space-y-8 mt-6">
              <div className="flex flex-row">
                <div>
                  <label htmlFor="email" className={labelClassName}>
                    How skilled would you rate your opponent at games?
                    <br></br>
                    Please enter a <strong>number</strong> between 0 and 100 
                    <br></br>
                    0 = not skilled at all, 100 = extremely skilled
                  </label>
                  <div className="mt-1">
                    <input
                      id="skill"
                      name="skill"
                      type="number"
                      autoComplete="off"
                      className={inputClassName}
                      value={skill}
                      onChange={(e) => setSkill(e.target.value)}
                    />
                  </div>
                </div>
                </div>
                <div className="flex flex-row">
                <div>
                  <label htmlFor="email" className={labelClassName}>
                    How fun was it to play against your opponent?
                    <br></br>
                    Please enter a <strong>number</strong> between 0 and 100 
                    <br></br>
                    0 = not fun at all, 100 = extremely fun
                  </label>
                  <div className="mt-1">
                    <input
                      id="funOpponent"
                      name="funOpponent"
                      type="number"
                      autoComplete="off"
                      className={inputClassName}
                      value={funOpponent}
                      onChange={(e) => setFunOpp(e.target.value)}
                    />
                  </div>
                </div>
              </div>
              {/* </div> */}
{/* 
              <div>
                <label className={labelClassName}>
                  Highest Education Qualification
                </label>
                <div className="grid gap-2">
                  <Radio
                    selected={education}
                    name="education"
                    value="high-school"
                    label="High School"
                    onChange={handleEducationChange}
                  />
                  <Radio
                    selected={education}
                    name="education"
                    value="bachelor"
                    label="US Bachelor's Degree"
                    onChange={handleEducationChange}
                  />
                  <Radio
                    selected={education}
                    name="education"
                    value="master"
                    label="Master's or higher"
                    onChange={handleEducationChange}
                  />
                  <Radio
                    selected={education}
                    name="education"
                    value="other"
                    label="Other"
                    onChange={handleEducationChange}
                  />
                </div>
              </div> */}

              <div className="grid grid-cols-3 gap-x-6 gap-y-3">

                <label className={labelClassName}>
                  Were there any hallmarks of games that you found particularly fun?
                </label>

                <label className={labelClassName}>
                  Were there any hallmarks of games that you found particularly NOT fun?
                </label>

                <label className={labelClassName}>
                  Did your game strategy evolve over the course of the experiment? If so, how?
                </label>

                

                <textarea
                  className={inputClassName}
                  dir="auto"
                  id="fun"
                  name="fun"
                  rows={4}
                  value={fun}
                  onChange={(e) => setFun(e.target.value)}
                />

                <textarea
                className={inputClassName}
                  dir="auto"
                  id="notFun"
                  name="notFun"
                  rows={4}
                  value={notFun}
                  onChange={(e) => setNotFun(e.target.value)}
                />

              <textarea
                className={inputClassName}
                  dir="auto"
                  id="strategy"
                  name="strategy"
                  rows={4}
                  value={strategy}
                  onChange={(e) => setStrategy(e.target.value)}
                />

                
              </div>


              <div className="grid grid-cols-2 gap-x-6 gap-y-2">


              <label className={labelClassName}>
                  How many moves ahead did you think about when playing? Just the current move? More than one move ahead?
              </label>


                <label className={labelClassName}>
                  Any other feedback? Did you ever consider pressing the Surrender button?
                </label>

              
              <textarea
                className={inputClassName}
                  dir="auto"
                  id="depth"
                  name="depth"
                  rows={4}
                  value={depth}
                  onChange={(e) => setDepth(e.target.value)}
                />

                <textarea
                  className={inputClassName}
                  dir="auto"
                  id="feedback"
                  name="feedback"
                  rows={4}
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                />

</div>

              <div className="mb-12">
                <Button type="submit">Submit</Button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}

export function Radio({ selected, name, value, label, onChange }) {
  return (
    <label className="text-sm font-medium text-gray-700">
      <input
        className="mr-2 shadow-sm sm:text-sm"
        type="radio"
        name={name}
        value={value}
        checked={selected === value}
        onChange={onChange}
      />
      {label}
    </label>
  );
}
