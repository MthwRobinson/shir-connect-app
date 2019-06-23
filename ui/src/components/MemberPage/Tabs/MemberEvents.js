import React, { Component } from 'react';
import { Table, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import moment from 'moment';

class MemberEvents extends Component {
  selectEvent = (eventID) => {
    // Switches to the participant page
    const url = '/event?id='+ eventID; 
    this.props.history.push(url);
  }

  render(){
    return(
      <div>
          <Row className='event-table'>
            <Table reponsive header hover>
              <thead>
                  <th className='table-heading'>#</th>
                  <th className='table-heading'>Event</th>
                  <th className='table-heading'>
                  Date
                  <i className='fa fa-caret-down paging-arrows'></i>
                  </th>
              </thead>
            <tbody>
              {this.props.member.events.map((event, index) => {
                return(
                  <tr 
                    className='table-row' 
                    key={index}
                    onClick={()=>this.selectEvent(event.participant_id)}
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
