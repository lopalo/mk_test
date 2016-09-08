import React from "react";

export default ({rowLimit, rowLimits, onChange}) => (
  <div className="form-group">
    <label className="control-label">
      <h6>Row Limit</h6>
    </label>
    <select value={rowLimit} className="form-control"
            onChange={e => onChange(parseInt(e.target.value))}>
      {rowLimits.map(rl =>
        <option key={rl} value={rl}>{rl}</option>
      )}
    </select>
  </div>
);
