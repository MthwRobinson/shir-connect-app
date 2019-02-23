import React, { Component } from 'react';
import { Table, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import moment from 'moment';

class Attendees extends Component {
  selectMember = (firstName, lastName) => {
    // Switches to the member page
    const url = '/member?firstName='+firstName+'&lastName='+lastName;
    this.props.history.push(url);
  }

  render(){
    return(
      <div>
          <Row className='event-table'>
            <Table reponsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'>#</th>
                  <th className='table-heading'>First Name</th>
                  <th className='table-heading'>
                  Last Name
                  <i className='fa fa-caret-down paging-arrows'></i>
                  </th>
                  <th className='table-heading'>Member</th>
                  <th className='table-heading'>Age</th>
                  <th className='table-heading'>Events</th>
                  <th className='table-heading'>First Event</th>
                </tr>
              </thead>
            <tbody>
              {this.props.event.attendees.map((attendee, index) => {
                return(
                  <tr 
                    className='table-row' 
                    key={index}
                    onClick={()=>this.selectMember(
                      attendee.first_name,
                      attendee.last_name
                    )}
                  >
                    <th>{index+1}</th>
                    <th>{attendee.first_name != null
                    ? attendee.first_name : ''}</th>
                    <th>{attendee.last_name != null
                    ? attendee.last_name : ''}</th>
                    <th>{attendee.is_member === true ? 'Y' : 'N'}</th>
                    <th>{attendee.age != null
                    ? attendee.age : ''}</th>
                    <th>{attendee.events_attended != null
                    ? attendee.events_attended : 0}</th>
                    <th>{attendee.first_event_date != null
                    ? moment(attendee.first_event_date).format('YYYY-MM-DD') : ''}</th>
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
export default withRouter(Attendees);
