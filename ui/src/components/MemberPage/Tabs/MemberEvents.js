import React, { Component } from 'react';
import { Table, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import moment from 'moment';

class MemberEvents extends Component {
  state = {
    ascending: false,
    sortColumn: 'start_datetime'
  }

  selectEvent = (eventID) => {
    // Switches to the participant page
    const url = '/event?id='+ eventID; 
    this.props.history.push(url);
  }
  
  handleSort = (sortColumn) => {
    // Handles the rearranging the sort order when a column is clicked
    let ascending = null;
    if(sortColumn===this.state.sortColumn){
      ascending = !this.state.ascending;
    } else {
      ascending = this.state.ascending;
    }
    this.setState({ascending: ascending, sortColumn: sortColumn});
    this.props.sortEvents(sortColumn, ascending);
  }

  render(){
    let sortArrow = this.state.ascending ? 'up' : 'down';
    const arrowClass = 'fa fa-caret-'+ sortArrow + ' paging-arrows';
    return(
      <div>
          <Row className='event-table'>
            <Table reponsive header hover>
              <thead>
                  <th className='table-heading'>#</th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('name')}>
                    Name
                    {this.state.sortColumn==='name'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('start_datetime')}>
                    Date
                    {this.state.sortColumn==='start_datetime'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
              </thead>
            <tbody>
              {this.props.member.events.map((event, index) => {
                return(
                  <tr 
                    className='table-row' 
                    key={index}
                    onClick={()=>this.selectEvent(event.event_id)}
                  >
                    <th>{index+1}</th>
                    <th>{event.name != null
                    ? event.name : ''}</th>
                    <th>{event.start_datetime!= null
                    ? moment(event.start_datetime).format('YYYY-MM-DD') : ''}</th>
                  </tr>
                )
              })}
            </tbody>
            </Table>
          </Row>
      </div> 
    )


  }
};
export default withRouter(MemberEvents);
