import React, { Component } from 'react';
import { Table, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

import moment from 'moment';

class Attendees extends Component {
  state = {
    ascending: true,
    sortColumn: 'last_name'
  }

  selectParticipant = (participantID) => {
    // Switches to the participant page
    const url = '/participant?id='+ participantID; 
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
    this.props.sortAttendees(sortColumn, ascending);
  }

  render(){
    let sortArrow = this.state.ascending ? 'up' : 'down';
    const arrowClass = 'fa fa-caret-'+ sortArrow + ' paging-arrows';
    return(
      <div>
          <Row className='event-table'>
            <Table reponsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'>#</th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('first_name')}>
                    First Name
                    {this.state.sortColumn === 'first_name'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('last_name')}>
                    Last Name
                    {this.state.sortColumn === 'last_name'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('is_member')}>
                    Member
                    {this.state.sortColumn === 'is_member'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('age')}>
                    Age
                    {this.state.sortColumn === 'age'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('events_attended')}>
                    Events
                    {this.state.sortColumn === 'events_attended'
                    ? <i className={arrowClass}></i>
                    : null}
                  </th>
                  <th className='table-heading'
                      onClick={()=>this.handleSort('first_event_date')}>
                    First Event
                    {this.state.sortColumn === 'first_event_date'
                    ? <i className={arrowClass}></i>
                    : null}
                 </th>
                </tr>
              </thead>
            <tbody>
              {this.props.event.attendees.map((attendee, index) => {
                return(
                  <tr 
                    className='table-row' 
                    key={index}
                    onClick={()=>this.selectParticipant(attendee.participant_id)}
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
