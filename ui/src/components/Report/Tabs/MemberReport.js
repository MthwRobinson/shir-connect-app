// Renders the information in the Members
// section of the report view
import moment from 'moment';
import React, { Component } from 'react';
import { Col, Row, Table } from 'react-bootstrap';
import Plot from 'react-plotly.js';
import { withRouter } from 'react-router-dom';

import Loading from './../../Loading/Loading';
import { DONUT_PLOT_COLORS } from './../../../utilities/plots';

class MemberReport extends Component {
  state = {
    'mounted': false
  }

  componentDidMount(){
    this.setState({mounted: true});
  }
  
  renderHouseholdTypeList = () => {
    // Shows the count for each location
    const households = this.props.householdType;
    let householdTypes = [];
    for(let group of households){
      householdTypes.push(<li><b>{group.member_type}:</b> {group.total}</li>);
    }
    return(
      <div>
        <ul className='quick-facts-bullets'>
          {householdTypes}
        </ul>
      </div>
    )
  }

  renderHouseholdTypes = () => {
    // Creates a donut chart showing the 
    // breakdown of household types
    
    // Generate the data for the plot
    const householdType = this.props.householdType;
    let values = [];
    let labels = [];
    for(let group of householdType){
      if(group.member_type !== 'All'){
        labels.push(group.member_type);
        values.push(group.total);
      }
    }
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: DONUT_PLOT_COLORS, color: 'white'}
    }]

    const householdTypeList = this.renderHouseholdTypeList();
    if(this.props.householdType.length === 0 || !this.state.mounted){
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Household Types</h4>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
        </Col>
      )
    } else {
      // Determine the size of the plot based on the size of the container
      const elem = document.getElementById('age-group-plot');
      const width = elem.clientWidth;
      const size = .5*width
      const layout = {
        height: size,
        width: size, 
        showlegend: false,
        margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
      }
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Household Types</h4>
          <div className='quick-facts-list'>
            {householdTypeList}
          </div>
          <div className='quick-facts-plot-area'> 
            <Plot
            data={data}
            layout={layout}
            style={{display: 'inline-block'}}
            config={{displayModeBar: false}}
            />
          </div>
        </div>
        </Col>
      )
    }
  }

  renderAgeGroupList = () => {
    // Shows the count for each demographic
    const demographics = this.props.demographics;
    let ageGroups = [];
    for(let group of demographics){
      if(group.age_group==='Young Professional'){
        ageGroups.push(<li><b>YP:</b> {group.total}</li>);
      } else {
        ageGroups.push(<li><b>{group.age_group}:</b> {group.total}</li>);
      }
    }
    return(
      <div>
        <ul className='quick-facts-bullets'>
          {ageGroups}
        </ul>
      </div>
    )

  }

  renderAgeGroups = () => {
    // Creates a donut chart showing the 
    // proportions of each age group
    
    // Generate the data for the plot
    const demographics = this.props.demographics;
    let values = [];
    let labels = [];
    for(let group of demographics){
      if(group.age_group !== 'All'){
        if(group.age_group==='Young Professional'){
          labels.push('YP');
        } else {
          labels.push(group.age_group);
        }
        values.push(group.total);
      }
    }
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: DONUT_PLOT_COLORS, color: 'white'}
    }]

    const ageGroupList = this.renderAgeGroupList();
    if(this.props.demographics.length === 0 || !this.state.mounted){
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Age Groups</h4>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
        </Col>
      )
    } else {
      // Determine the size of the plot based on the size of the container
      const elem = document.getElementById('age-group-plot');
      const width = elem.clientWidth;
      const size = .5*width
      const layout = {
        height: size,
        width: size, 
        showlegend: false,
        margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
      }
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Age Groups</h4>
          <div className='quick-facts-list'>
            {ageGroupList}
          </div>
          <div className='quick-facts-plot-area'> 
            <Plot
            data={data}
            layout={layout}
            style={{display: 'inline-block'}}
            config={{displayModeBar: false}}
            />
          </div>
        </div>
        </Col>
      )
    }
  }
  
  renderNewMemberAgeGroupList = () => {
    // Shows the count for each demographic
    const demographics = this.props.newMemberDemographics;
    let ageGroups = [];
    for(let group of demographics){
      if(group.age_group==='Young Professional'){
        ageGroups.push(<li><b>YP:</b> {group.total}</li>);
      } else {
        ageGroups.push(<li><b>{group.age_group}:</b> {group.total}</li>);
      }
    }
    return(
      <div>
        <ul className='quick-facts-bullets'>
          {ageGroups}
        </ul>
      </div>
    )

  }
  
  renderNewMemberDemographics = () => {
    // Creates a donut chart showing the 
    // proportions of each age group
    
    // Generate the data for the plot
    const demographics = this.props.newMemberDemographics;
    let values = [];
    let labels = [];
    for(let group of demographics){
      if(group.age_group !== 'All'){
        if(group.age_group==='Young Professional'){
          labels.push('YP');
        } else {
          labels.push(group.age_group);
        }
        values.push(group.total);
      }
    }
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: DONUT_PLOT_COLORS, color: 'white'}
    }]

    const ageGroupList = this.renderNewMemberAgeGroupList();
    if(this.props.demographics.length === 0 || !this.state.mounted){
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>New Members (Past Year)</h4>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
        </Col>
      )
    } else {
      // Determine the size of the plot based on the size of the container
      const elem = document.getElementById('age-group-plot');
      const width = elem.clientWidth;
      const size = .5*width
      const layout = {
        height: size,
        width: size, 
        showlegend: false,
        margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
      }
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>New Members (Past Year)</h4>
          <div className='quick-facts-list'>
            {ageGroupList}
          </div>
          <div className='quick-facts-plot-area'> 
            <Plot
            data={data}
            layout={layout}
            style={{display: 'inline-block'}}
            config={{displayModeBar: false}}
            />
          </div>
        </div>
        </Col>
      )
    }
  }
  
  renderLocationList = (key) => {
    // Shows the count for each location
    const memberLocations = this.props.memberLocations[key];
    let ageGroups = [];
    for(let group of memberLocations){
      if(group.location==='Young Professional'){
        ageGroups.push(<li><b>YP:</b> {group.total}</li>);
      } else {
        ageGroups.push(<li><b>{group.location}:</b> {group.total}</li>);
      }
    }
    return(
      <div>
        <ul className='quick-facts-bullets'>
          {ageGroups}
        </ul>
      </div>
    )
  }

  renderMemberLocations = (key) => {
    // Creates a donut chart showing the 
    // proportions of each age group
    
    // Generate the data for the plot
    const memberLocations = this.props.memberLocations[key];
    let values = [];
    let labels = [];
    for(let group of memberLocations){
      if(group.location !== 'All'){
        labels.push(group.location);
        values.push(group.total);
      }
    }
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: DONUT_PLOT_COLORS, color: 'white'}
    }]

    const locationList = this.renderLocationList(key);
    if(this.props.memberLocations.length === 0 || !this.state.mounted){
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Locations</h4>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
        </Col>
      )
    } else {
      // Determine the size of the plot based on the size of the container
      const elem = document.getElementById('age-group-plot');
      const width = elem.clientWidth;
      const size = .5*width
      const layout = {
        height: size,
        width: size, 
        showlegend: false,
        margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
      }
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Locations</h4>
          <div className='quick-facts-list'>
            {locationList}
          </div>
          <div className='quick-facts-plot-area'> 
            <Plot
            data={data}
            layout={layout}
            style={{display: 'inline-block'}}
            config={{displayModeBar: false}}
            />
          </div>
        </div>
        </Col>
      )
    }
  }

  renderNewMembers = () => {
    // Creates a table that displays the most recent members
    if(this.props.newMembers.length === 0 || !this.state.mounted){
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
        </Col>
      )
    } else {
      const rows = this.renderTableRows();
      return(
        <Table responsive header hover>
          <thead>
            <tr>
              <th className='table-heading'>First Name</th>
              <th className='table-heading'>Last Name</th>
              <th className='table-heading'>Age</th>
              <th className='table-heading'>City</th>
              <th className='table-heading'>State</th>
              <th className='table-heading'>Joined</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </Table>
      )
    }
  }

  selectMember = (firstName, lastName) => {
    // Navigates to the page for the member
    const url = '/member?firstName='+firstName+'&lastName='+lastName;
    this.props.history.push(url);
  }

  renderTableRows = () => {
    // Renders the rows for the new members table
    let rows = [];
    let i = 0;
    for(let member of this.props.newMembers){
      i++;
      const row = (
        <tr className='table-row' key={i}
            onClick={()=>this.selectMember(member.first_name, 
                                           member.last_name)} >
          <th>{member.first_name != null
              ? member.first_name : '--'}</th>
          <th>{member.last_name != null
              ? member.last_name : '--'}</th>
          <th>{member.age != null
              ? member.age : null}</th>
          <th>{member.city != null
              ? member.city : null}</th>
          <th>{member.region != null
              ? member.region : null}</th>
          <th>{member.membership_date != null
              ? moment(member.membership_date).format('MM/DD/YY')
              : null}</th>
        </tr>
      )
      rows.push(row);
    }
    return rows
  }
  
  renderNewMemberCount= () => {
    // Creates a bar chart with the number o new members by quarter 
    // Generate the data for the plot
    const newMemberCount= this.props.newMemberCount;
    let values = [];
    let labels = [];
    for(let group in newMemberCount){
      labels.push(group);
      values.push(newMemberCount[group]);
    }
    const data = [{
      y: values,
      x: labels,
      type: 'bar',
      textinfo: 'label',
      marker: {colors: DONUT_PLOT_COLORS}
    }]

    if(this.props.memberLocations.length === 0 || !this.state.mounted){
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>New Household Count</h4>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
        </Col>
      )
    } else {
      // Determine the size of the plot based on the size of the container
      const elem = document.getElementById('age-group-plot');
      const width = elem.clientWidth;
      const layout = {
        height: .55*width,
        width: .9*width,
        yaxis: {
          title: 'New Households',
          titlefont: {family: 'Source Sans Pro'}
        },
        xaxis: { tickangle: 45 },
        showlegend: false,
        margin: {l: 50, r: 35, b: 70, t: 0, pad: 0}
      }
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>New Household Count</h4>
          <div className='quick-facts-plot-area'> 
            <Plot
            data={data}
            layout={layout}
            style={{display: 'inline-block'}}
            config={{displayModeBar: false}}
            />
          </div>
        </div>
        </Col>
      )
    }
  }
  
  renderHouseholdCount= () => {
    // Creates a bar chart with the number of households by year
    const newMemberCount= this.props.householdCount
    let values = [];
    let labels = [];
    for(let group of newMemberCount){
      labels.push(group.year);
      values.push(group.count);
    }
    const data = [{
      y: values,
      x: labels,
      type: 'bar',
      textinfo: 'label',
      marker: {colors: DONUT_PLOT_COLORS}
    }]

    if(this.props.memberLocations.length === 0 || !this.state.mounted){
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Household Count</h4>
          <div className='event-loading'>
            <Loading />
          </div>
        </div>
        </Col>
      )
    } else {
      // Determine the size of the plot based on the size of the container
      const elem = document.getElementById('age-group-plot');
      const width = elem.clientWidth;
      const layout = {
        height: .55*width,
        width: .9*width,
        yaxis: {
          title: 'Households',
          titlefont: {family: 'Source Sans Pro'}
        },
        xaxis: { tickangle: 45 },
        showlegend: false,
        margin: {l: 50, r: 35, b: 70, t: 0, pad: 0}
      }
      return(
        <Col xs={6} sm={6} md={6} lg={6} id='age-group-plot'>
        <div className='quick-facts-plot-container'>
          <h4>Household Count</h4>
          <div className='quick-facts-plot-area'> 
            <Plot
            data={data}
            layout={layout}
            style={{display: 'inline-block'}}
            config={{displayModeBar: false}}
            />
          </div>
        </div>
        </Col>
      )
    }
  }
  
  render(){
    const ageGroups = this.renderAgeGroups();
    const memberLocations = this.renderMemberLocations('all_members');
    const newMemberLocations = this.renderMemberLocations('new_members');
    // const newMembers = this.renderNewMembers();
    const newMemberCount = this.renderNewMemberCount();
    const newMemberDemographics = this.renderNewMemberDemographics();
    const householdCount = this.renderHouseholdCount();
    const householdType = this.renderHouseholdTypes();
   return(
      <div className='QuickFacts'>
        <h2>Membership Report</h2><hr/>
        <h3>Household Demographics</h3>
        <Row>
          {householdCount}
          {householdType}
        </Row>
        <h3>Member Demographics</h3>
        <Row>
          {ageGroups}
          {memberLocations}
        </Row><hr/>
        <h3>New Members</h3>
        <Row>
          {newMemberDemographics}
          {newMemberLocations}
        </Row>
        <Row>
          {newMemberCount}
        </Row>
        {/* <h4>Newest Members</h4><br/> */}
        {/* {newMembers} */}
      </div> 
    )
  }
};
export default withRouter(MemberReport);
