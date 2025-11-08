package com.crosspostme.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.crosspostme.data.model.*
import com.crosspostme.data.repository.AdsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for Ads management
 * Following MVVM architecture patterns and reactive programming with StateFlow
 */
@HiltViewModel
class AdsViewModel @Inject constructor(
    private val adsRepository: AdsRepository
) : ViewModel() {

    // UI State data classes
    data class AdsUiState(
        val ads: List<Ad> = emptyList(),
        val isLoading: Boolean = false,
        val error: String? = null
    )

    data class DashboardUiState(
        val stats: DashboardStats? = null,
        val isLoading: Boolean = false,
        val error: String? = null
    )

    // Private mutable state
    private val _adsUiState = MutableStateFlow(AdsUiState())
    private val _dashboardUiState = MutableStateFlow(DashboardUiState())
    private val _selectedAd = MutableStateFlow<Ad?>(null)

    // Public read-only state
    val adsUiState: StateFlow<AdsUiState> = _adsUiState.asStateFlow()
    val dashboardUiState: StateFlow<DashboardUiState> = _dashboardUiState.asStateFlow()
    val selectedAd: StateFlow<Ad?> = _selectedAd.asStateFlow()

    init {
        loadAds()
        loadDashboardStats()
    }

    // Load all ads
    fun loadAds(status: String? = null, platform: String? = null) {
        viewModelScope.launch {
            _adsUiState.update { it.copy(isLoading = true, error = null) }
            
            adsRepository.getAds(status, platform)
                .catch { exception ->
                    _adsUiState.update { 
                        it.copy(
                            isLoading = false, 
                            error = exception.message ?: "Unknown error occurred"
                        ) 
                    }
                }
                .collect { result ->
                    result.fold(
                        onSuccess = { ads ->
                            _adsUiState.update { 
                                it.copy(ads = ads, isLoading = false, error = null) 
                            }
                        },
                        onFailure = { exception ->
                            _adsUiState.update { 
                                it.copy(
                                    isLoading = false, 
                                    error = exception.message ?: "Failed to load ads"
                                ) 
                            }
                        }
                    )
                }
        }
    }

    // Create new ad
    fun createAd(adCreate: AdCreate) {
        viewModelScope.launch {
            _adsUiState.update { it.copy(isLoading = true, error = null) }
            
            val result = adsRepository.createAd(adCreate)
            result.fold(
                onSuccess = { newAd ->
                    // Add new ad to existing list
                    val currentAds = _adsUiState.value.ads.toMutableList()
                    currentAds.add(0, newAd)
                    _adsUiState.update { 
                        it.copy(ads = currentAds, isLoading = false, error = null) 
                    }
                },
                onFailure = { exception ->
                    _adsUiState.update { 
                        it.copy(
                            isLoading = false, 
                            error = exception.message ?: "Failed to create ad"
                        ) 
                    }
                }
            )
        }
    }

    // Update existing ad
    fun updateAd(adId: String, adUpdate: AdUpdate) {
        viewModelScope.launch {
            val result = adsRepository.updateAd(adId, adUpdate)
            result.fold(
                onSuccess = { updatedAd ->
                    // Update ad in the list
                    val currentAds = _adsUiState.value.ads.toMutableList()
                    val index = currentAds.indexOfFirst { it.id == adId }
                    if (index != -1) {
                        currentAds[index] = updatedAd
                        _adsUiState.update { it.copy(ads = currentAds) }
                    }
                },
                onFailure = { exception ->
                    _adsUiState.update { 
                        it.copy(error = exception.message ?: "Failed to update ad") 
                    }
                }
            )
        }
    }

    // Delete ad
    fun deleteAd(adId: String) {
        viewModelScope.launch {
            val result = adsRepository.deleteAd(adId)
            result.fold(
                onSuccess = {
                    // Remove ad from the list
                    val currentAds = _adsUiState.value.ads.filter { it.id != adId }
                    _adsUiState.update { it.copy(ads = currentAds) }
                },
                onFailure = { exception ->
                    _adsUiState.update { 
                        it.copy(error = exception.message ?: "Failed to delete ad") 
                    }
                }
            )
        }
    }

    // Post ad to platform
    fun postAd(adId: String, platform: String) {
        viewModelScope.launch {
            _adsUiState.update { it.copy(isLoading = true, error = null) }
            
            val result = adsRepository.postAd(adId, platform)
            result.fold(
                onSuccess = { postedAd ->
                    // Update ad status in the list
                    val currentAds = _adsUiState.value.ads.toMutableList()
                    val index = currentAds.indexOfFirst { it.id == adId }
                    if (index != -1) {
                        currentAds[index] = currentAds[index].copy(status = "posted")
                        _adsUiState.update { 
                            it.copy(ads = currentAds, isLoading = false, error = null) 
                        }
                    }
                },
                onFailure = { exception ->
                    _adsUiState.update { 
                        it.copy(
                            isLoading = false, 
                            error = exception.message ?: "Failed to post ad"
                        ) 
                    }
                }
            )
        }
    }

    // Load dashboard stats
    fun loadDashboardStats() {
        viewModelScope.launch {
            _dashboardUiState.update { it.copy(isLoading = true, error = null) }
            
            adsRepository.getDashboardStats()
                .catch { exception ->
                    _dashboardUiState.update { 
                        it.copy(
                            isLoading = false, 
                            error = exception.message ?: "Unknown error occurred"
                        ) 
                    }
                }
                .collect { result ->
                    result.fold(
                        onSuccess = { stats ->
                            _dashboardUiState.update { 
                                it.copy(stats = stats, isLoading = false, error = null) 
                            }
                        },
                        onFailure = { exception ->
                            _dashboardUiState.update { 
                                it.copy(
                                    isLoading = false, 
                                    error = exception.message ?: "Failed to load dashboard stats"
                                ) 
                            }
                        }
                    )
                }
        }
    }

    // Select ad for detailed view
    fun selectAd(ad: Ad) {
        _selectedAd.value = ad
    }

    // Clear selected ad
    fun clearSelectedAd() {
        _selectedAd.value = null
    }

    // Clear error messages
    fun clearError() {
        _adsUiState.update { it.copy(error = null) }
        _dashboardUiState.update { it.copy(error = null) }
    }
}