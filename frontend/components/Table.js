import React from "react";

export default ({data}) => (
  <table className="table">
    <thead>
      <tr>
        <th>#</th>
        <th>Object ID</th>
        <th>Description</th>
        <th>Status</th>
        <th>x</th>
        <th>y</th>
        <th>Online</th>
      </tr>
    </thead>
    <tbody>
      {data.map((row, idx) => (
        <ListItem key={row.object_id} row={row} idx={idx}/>
      ))}
    </tbody>
  </table>
);


const ListItem = ({row, idx}) => (
  <tr className={row.online === "online" ? "" : "warning"}>
    <td>{idx}</td>
    <td>{row.object_id}</td>
    <td>{row.description}</td>
    <td>{row.status}</td>
    <td>{row.x}</td>
    <td>{row.y}</td>
    <td>
      {<span className={"glyphicon " + (row.online == "offline" ?
                                        "glyphicon-remove text-danger" :
                                        "glyphicon-ok text-success")}>
       </span>}
    </td>
  </tr>
);


