import React from "react";

import Table from "./Table";
import Selector from "./Selector";


export default class Live extends React.Component {
    constructor(props) {
        super(props);
        this._ws = null;
        this.state = {
            rowLimit: 0,
            rowLimits: [],
            data: []
        };
        this.setLimit = this.setLimit.bind(this);
    }
    componentDidMount() {
        this._ws = new WebSocket(`ws://${window.location.host}/listen`);
        this._ws.onopen = () => this.updateLimit();
        this._ws.onmessage = e => this.setState({data: JSON.parse(e.data)});
        fetch("row-limits")
            .then(resp => resp.json())
            .then(data => {
                let rowLimits = data.row_limits;
                this.setState({rowLimits});
                this.setLimit(rowLimits[0]);
            });

    }
    componentWillUnmount() {
        this._ws.onmessage = null;
        this._ws.open = null;
        delete this._ws;
    }
    updateLimit() {
        if (this._ws.readyState !== 1) return;
        let limit = this.state.rowLimit;
        this._ws.send(JSON.stringify(["set-limit", limit]));
    }
    setLimit(rowLimit) {
        this.setState({rowLimit}, () => this.updateLimit());
    }
    render() {
        return (
          <div className="row">
            <div className="col-md-2">
              <Selector {...this.state} onChange={this.setLimit} />
            </div>
            <div className="col-md-10">
               <Table data={this.state.data} />;
            </div>
          </div>
        );
    }
}





