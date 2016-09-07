import React from "react";


export default class Live extends React.Component {
    constructor(props) {
        super(props);
        this._ws = null;
        this.state = {
            rowLimit: 10,
            rowLimits: [],
            data: []
        };
    }
    componentDidMount() {
        this._ws = new WebSocket(`ws://${window.location.host}/listen`);
        this._ws.onopen = () => this.setLimit();
        this._ws.onmessage = e => this.setState({data: JSON.parse(e.data)});
        fetch("row-limits")
            .then(resp => resp.json())
            .then(data => {
                let rowLimits = data.row_limits;
                this.setState({rowLimits, rowLimit: rowLimits[0]});
                this.setLimit();
            });

    }
    componentWillUnmount() {
        this._ws.onmessage = null;
        this._ws.open = null;
        delete this._ws;
    }
    setLimit() {
        if (this._ws.readyState !== 1) return;
        let limit = this.state.rowLimit;
        this._ws.send(JSON.stringify(["set-limit", limit]));
    }
    render() {
        return <Table data={this.state.data} />;
    }
}

const Table = ({data}) => (
  <table className="table">
    <thead>
      <tr>
        <th>Object ID</th>
        <th>Description</th>
        <th>Status</th>
        <th>x</th>
        <th>y</th>
        <th>Online</th>
      </tr>
    </thead>
    <tbody>
      {data.map(row => <ListItem key={row.object_id} row={row} />)}
    </tbody>
  </table>
);


const ListItem = ({row}) => (
  <tr className={row.online === "online" ? "" : "warning"}>
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


