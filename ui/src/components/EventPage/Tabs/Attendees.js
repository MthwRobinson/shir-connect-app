import React, { Component } from 'react';
import { Table, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';

class Attendees extends Component {
  render(){
    return(
      <div>
          <Row className='event-table'>
            <Table reponsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'>First Name</th>
                  <th className='table-heading'>
                  Last Name
                  <i className='fa fa-caret-down paging-arrows'></i>
                  </th>
                  <th className='table-heading'>E-mail</th>
                  <th className='table-heading'>Age</th>
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
                    <th>{attendee.first_name != null
                    ? attendee.first_name : '--'}</th>
                    <th>{attendee.last_name != null
                    ? attendee.last_name : '--'}</th>
                    <th>{attendee.email != null
                    ? attendee.email : '--'}</th>
                    <th>{attendee.age != null
                    ? attendee.age : ''}</th>
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
